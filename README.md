# nuc-fan-rpm

A tiny Python script that prints the current fan speed (RPM) of an Intel NUC. It reads the speed from the embedded controller (EC) memory window through `/dev/mem`. It only reads and never writes.

The EC layout comes from VirtualSMC's `Intel_EC_V9` / `SPG_EC` support.

## Tested on

- Intel NUC10i5FNK (Frost Canyon, NUC10) running Proxmox VE (Debian-based kernel).

It is probably the same EC on NUC8, NUC10 and NUC11 boards whose EC ID at offset `+0x400` is `SPG_EC` or `ELM_EC`, but that has **not been verified**. If the ID doesn't match, the script refuses to read anything.

## Requirements

- root
- Linux on x86
- `python3`
- `setpci` (from `pciutils`). Optional: without it, the script falls back to the default base `0xFE410000`.
- **Secure Boot OFF.** Kernel lockdown blocks `/dev/mem`. Check that `/sys/kernel/security/lockdown` shows `[none]`.
- The kernel must allow `/dev/mem` access to that MMIO range. With `CONFIG_STRICT_DEVMEM` enabled it still worked on the Proxmox kernel, because the range isn't System RAM.

## Usage

```sh
sudo ./nuc-fan.py
```

Output:

- Success: one integer, the fan RPM (e.g. `1834`), exit code 0.
- Failure: one line starting with `ERR` (e.g. `ERR bad EC id ...`, `ERR fan flag 0`, `ERR mmap: ...`), exit code 1.

This makes it easy to use from monitoring scripts, Prometheus textfile collectors, etc.

## How it works

1. Reads LPC bridge (`00:1f.0`) config register `0x98` with `setpci`. If the enable bit is set, the upper bits give the EC memory window base, normally `0xFE410000`.
2. Maps one page at that base read-only from `/dev/mem`.
3. Checks the EC ID string at `+0x400` (`SPG_EC` or `ELM_EC`).
4. Checks that the fan-present flag at `+0x41A` == 1.
5. Reads the RPM as a big-endian u16 at `+0x41B`.

## Disclaimer

Provided as-is, with no warranty of any kind. The script only reads memory and never writes to the EC, but you use it at your own risk.

## License

MIT. See [LICENSE](LICENSE).
