"""Entry point for python -m wezterm_tui."""

from wezterm_tui.app import WezTermSettingsApp


def main():
    app = WezTermSettingsApp()
    app.run()


if __name__ == "__main__":
    main()
