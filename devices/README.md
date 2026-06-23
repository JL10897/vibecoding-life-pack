# Device Overrides

Device overrides are for differences that should not become the shared default.

## Directory Naming

Use a stable device id:

```text
devices/<device-id>/
```

Examples:

```text
devices/home-linux/
devices/work-devcloud/
devices/macbook/
```

Set the id with:

```bash
export VIBE_DEVICE_ID=work-devcloud
```

If `VIBE_DEVICE_ID` is not set, scripts derive one from `hostname`.

## Override Rules

- Keep overrides small.
- Explain why an override exists in `manifest.override.yaml`.
- Do not duplicate full canonical directories unless unavoidable.
- Promote reusable changes into `canonical/`.

## Example

```yaml
device:
  id: work-devcloud
  note: Remote Linux dev machine.

overrides:
  - agent: cursor
    path: devices/work-devcloud/cursor/settings
    reason: Uses remote-specific paths.
```

## Promotion Flow

```text
identify reusable override -> move behavior into canonical -> remove override -> update manifest -> run merge check -> autosave
```
