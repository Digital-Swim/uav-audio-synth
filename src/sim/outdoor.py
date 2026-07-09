
from src.config.data_classes import ScenarioConfig
from src.sim.mics import MicrophoneArray
import numpy as np
import pyroomacoustics as pra


class OutdoorAcousticSim:
    """
    Simulates sound propagation in an outdoor urban environment using
    a large ShoeBox room with:
      • Concrete/brick walls  → specular reflections (buildings)
      • Asphalt/concrete floor → partial reflection
      • Anechoic ceiling      → open sky, no top reflection
      • Air absorption        → high-frequency roll-off with distance
      • max_order=3           → up to 3rd-order reflections (realistic for
                                nearby building facades at 10–100 m)

    Moving-source approximation
    ---------------------------
    The drone trajectory is split into n_rir_snapshots segments.
    For each snapshot we build one RIR from the midpoint position,
    convolve the corresponding audio slice, then overlap-add with
    a Hann cross-fade window.  This gives a smooth, physically
    consistent time-varying transfer function without per-sample room solves.
    """

    def __init__(self, cfg: ScenarioConfig, mic_array: MicrophoneArray):
        self.cfg   = cfg
        self.oc    = cfg.outdoor
        self.sc    = cfg.sim
        self.mic   = mic_array

    # ── public ────────────────────────────────────────────────────────────────

    def simulate(
        self,
        source_signal: np.ndarray,   # (N,) float32
        positions:     np.ndarray,   # (N, 3)
    ) -> np.ndarray:
        N       = len(source_signal)
        n_mics  = self.mic.n
        n_snaps = self.sc.n_rir_snapshots
        
        # Allocate output buffer with extra space for the final RIR tail
        output  = np.zeros((N + int(self.sc.fs * 0.5), n_mics), dtype=np.float64)

        # 1. Setup a strict Overlap-Add framework
        # We will use a 50% overlap windowing strategy to guarantee perfect reconstruction.
        # block_size is the total window length, hop_size is how much we move forward.
        hop_size   = int(np.ceil(N / (n_snaps + 1)))
        block_size = hop_size * 2  # 50% overlap means window is twice the hop size
        
        # Create a perfect Hann window for 50% overlap
        # Hann window satisfies the Constant Amplitude property when shifted by half its length
        window = np.hanning(block_size)

        for k in range(n_snaps):
            # Calculate the exact sample range for this window
            s_ext = k * hop_size
            e_ext = s_ext + block_size
            
            # If the window goes past the signal, pad the signal with zeros
            if s_ext >= N:
                break
                
            signal_slice = source_signal[s_ext:e_ext]
            if len(signal_slice) < block_size:
                # Pad with zeros if it's the final partial block
                signal_slice = np.pad(signal_slice, (0, block_size - len(signal_slice)))
            
            # Find the midpoint position of this specific slice
            mid_idx = min(s_ext + hop_size, N - 1)
            pos = positions[mid_idx]
            
            # Convolve only this windowed slice
            rir_sigs = self._single_rir_convolve(
                signal_slice * window, pos, n_mics
            )  # Shape: (n_mics, block_size + rir_tail)
            
            # Accumulate into output channel by channel
            for m in range(n_mics):
                seg = rir_sigs[m]
                
                # Check available space in our total output buffer
                available_space = len(output) - s_ext
                if len(seg) > available_space:
                    seg = seg[:available_space]
                    
                output[s_ext : s_ext + len(seg), m] += seg

        # Trim back to original length N
        output = output[:N, :]
        
        # Normalize
        peak = np.max(np.abs(output)) + 1e-12
        return (output / peak * 0.9).astype(np.float32)
    
    
    def simulate1(
        self,
        source_signal: np.ndarray,   # (N,) float32
        positions:     np.ndarray,   # (N, 3)
    ) -> np.ndarray:
        N       = len(source_signal)
        n_mics  = self.mic.n
        n_snaps = self.sc.n_rir_snapshots
        
        # We need a slightly longer output to accommodate the final RIR tail
        # or we truncate at N. Let's allocate a buffer and truncate at the end.
        output  = np.zeros((N + int(self.sc.fs * 0.5), n_mics), dtype=np.float64)

        # Define snapshot intervals with an overlap of 'fade'
        fade = min(512, N // (n_snaps * 4))
        
        # Calculate block size per snapshot
        block_size = int(np.ceil(N / n_snaps))
        
        for k in range(n_snaps):
            # Calculate the core sample range for this snapshot
            s_core = k * block_size
            e_core = min(s_core + block_size, N)
            if s_core >= N:
                break
                
            # Extend the window backward and forward by 'fade' for smooth merging
            s_ext = max(0, s_core - fade)
            e_ext = min(N, e_core + fade)
            
            # Extract the slice of audio and find the midpoint position
            signal_slice = source_signal[s_ext:e_ext]
            mid_idx = (s_ext + e_ext) // 2
            pos = positions[mid_idx]
            
            # Convolve ONLY this slice
            # Note: Modify _single_rir_convolve to accept 'signal_slice' instead of 'source_signal'
            rir_sigs = self._single_rir_convolve(
                signal_slice, pos, n_mics
            )  # Shape: (n_mics, len(signal_slice) + rir_tail)
            
            # Create a cross-fade window matching the extended slice length
            window = np.ones(e_ext - s_ext)
            if s_ext > 0:  # Fade-in if not the very first sample
                window[:fade] = np.hanning(fade * 2)[:fade]
            if e_ext < N:  # Fade-out if not the very last sample
                window[-fade:] = np.hanning(fade * 2)[fade:]
                
            # Apply window and accumulate into the output channel by channel
            for m in range(n_mics):
                # The convolution output length is longer than the input slice due to the RIR tail
                tail_len = rir_sigs.shape[1] - len(signal_slice)
                
                # Apply window to the execution part, leave the tail to decay naturally
                seg = rir_sigs[m].copy()
                seg[:len(window)] *= window
                
                # Figure out how much space is actually left in the output array
                available_space = len(output) - s_ext
                if len(seg) > available_space:
                    seg = seg[:available_space]  # Truncate the tail if it exceeds the buffer
                
                # Add to output at the correct time offset
                output[s_ext : s_ext + len(seg), m] += seg

        # Trim back to original length N and normalize
        output = output[:N, :]
        peak = np.max(np.abs(output)) + 1e-12
        return (output / peak * 0.9).astype(np.float32)
    
    
    def simulate11(
        self,
        source_signal: np.ndarray,   # (N,) float32
        positions:     np.ndarray,   # (N, 3)
    ) -> np.ndarray:
        """
        Returns (N, n_mics) float32 multichannel signal.
        """
        N       = len(source_signal)
        n_mics  = self.mic.n
        n_snaps = self.sc.n_rir_snapshots
        output  = np.zeros((N, n_mics), dtype=np.float64)

        snap_edges  = np.linspace(0, N, n_snaps + 1, dtype=int)
        snap_starts = snap_edges[:-1]
        snap_ends   = snap_edges[1:]

        fade = min(512, (snap_ends[0] - snap_starts[0]) // 4)

        for k in range(n_snaps):
            s, e    = snap_starts[k], snap_ends[k]
            mid_idx = (s + e) // 2
            pos     = positions[mid_idx]

            rir_sigs = self._single_rir_convolve(
                source_signal, pos, n_mics
            )  # (n_mics, N + rir_tail)

            # Overlap-add slice into output
            for m in range(n_mics):
                ch  = rir_sigs[m]
                seg = ch[:N]  # trim to N
                if len(seg) < N:
                    seg = np.pad(seg, (0, N - len(seg)))
                output[:, m] += seg

            if k % max(1, n_snaps // 5) == 0:
                log.debug(f"  RIR snapshot {k+1}/{n_snaps}")

        # Per-channel normalise
        peak = np.max(np.abs(output)) + 1e-12
        output = (output / peak * 0.9).astype(np.float32)
        return output

    # ── private ───────────────────────────────────────────────────────────────

    def _build_room(self) -> pra.ShoeBox:
        oc  = self.oc
        mat = pra.make_materials(
            east=oc.wall_material,
            west=oc.wall_material,
            north=oc.wall_material,
            south=oc.wall_material,
            floor=oc.ground_material,
            ceiling=oc.sky_material,
        )
        return pra.ShoeBox(
            [oc.width, oc.depth, oc.height],
            fs=self.sc.fs,
            materials=mat,
            max_order=oc.max_rir_order,
            air_absorption=oc.air_absorption,
            ray_tracing=False,
        )

    def _clamp_pos(self, pos: np.ndarray) -> np.ndarray:
        m = 0.5
        lo = [m, m, m]
        hi = [self.oc.width - m, self.oc.depth - m, self.oc.height - m]
        return np.clip(pos, lo, hi)

    def _single_rir_convolve(
        self,
        signal: np.ndarray,   # (N,) float32
        pos:    np.ndarray,   # (3,)
        n_mics: int,
    ) -> np.ndarray:
        """Build one room, one source position, return (n_mics, N+tail)."""
        room = self._build_room()
        room.add_microphone_array(
            self.mic.positions,
            directivity=self.mic.directivities,
        )
        room.add_source(
            self._clamp_pos(pos).tolist(),
            signal=signal,
        )
        room.simulate()
        return room.mic_array.signals.astype(np.float64)   # (n_mics, L)

