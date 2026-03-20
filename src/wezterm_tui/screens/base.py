"""Base class for settings screens."""

from __future__ import annotations

from textual.containers import VerticalScroll
from textual.widgets import Static, Input, Select, Switch, Label

from wezterm_tui.schema import Option, OptionType, get_category_options


class SettingsScreen(VerticalScroll):
    """Base screen that auto-generates form widgets from schema options."""

    CATEGORY: str = ""

    def __init__(self, settings: dict, **kwargs):
        super().__init__(**kwargs)
        self.settings = settings
        self.options = get_category_options(self.CATEGORY)

    def get_value(self, option: Option):
        if option.type == OptionType.KEYBINDINGS:
            return self.settings.get("keybindings", [])
        cat_data = self.settings.get(option.category, {})
        return cat_data.get(option.key, option.default)

    def set_value(self, option: Option, value):
        if option.type == OptionType.KEYBINDINGS:
            self.settings["keybindings"] = value
            return
        self.settings.setdefault(option.category, {})[option.key] = value

    def compose_field(self, option: Option):
        value = self.get_value(option)
        field_id = f"field-{option.category}-{option.key}"

        yield Label(option.label)

        match option.type:
            case OptionType.BOOL:
                yield Switch(value=value, id=field_id)
            case OptionType.ENUM:
                options = [(v, v) for v in option.enum_values]
                yield Select(options, value=value, id=field_id, allow_blank=False)
            case OptionType.INT | OptionType.FLOAT:
                yield Input(value=str(value), id=field_id)
            case OptionType.STRING:
                yield Input(value=str(value), id=field_id)
            case OptionType.STRING_LIST:
                yield Input(value=", ".join(value) if isinstance(value, list) else str(value),
                            id=field_id, placeholder="Comma-separated values")
            case OptionType.PADDING:
                for side in ("left", "right", "top", "bottom"):
                    yield Label(f"  {side.capitalize()}")
                    yield Input(value=str(value.get(side, 0)), id=f"{field_id}-{side}")

    def compose(self):
        yield Static(f" {self.CATEGORY.upper()} SETTINGS ", classes="screen-title")
        for option in self.options:
            yield from self.compose_field(option)

    def collect_values(self) -> dict:
        for option in self.options:
            field_id = f"field-{option.category}-{option.key}"
            try:
                match option.type:
                    case OptionType.BOOL:
                        widget = self.query_one(f"#{field_id}", Switch)
                        self.set_value(option, widget.value)
                    case OptionType.ENUM:
                        widget = self.query_one(f"#{field_id}", Select)
                        if widget.value is not Select.BLANK:
                            self.set_value(option, widget.value)
                    case OptionType.INT:
                        widget = self.query_one(f"#{field_id}", Input)
                        try:
                            self.set_value(option, int(widget.value))
                        except ValueError:
                            pass
                    case OptionType.FLOAT:
                        widget = self.query_one(f"#{field_id}", Input)
                        try:
                            self.set_value(option, float(widget.value))
                        except ValueError:
                            pass
                    case OptionType.STRING:
                        widget = self.query_one(f"#{field_id}", Input)
                        self.set_value(option, widget.value)
                    case OptionType.STRING_LIST:
                        widget = self.query_one(f"#{field_id}", Input)
                        values = [v.strip() for v in widget.value.split(",") if v.strip()]
                        self.set_value(option, values)
                    case OptionType.PADDING:
                        pad = {}
                        for side in ("left", "right", "top", "bottom"):
                            w = self.query_one(f"#{field_id}-{side}", Input)
                            try:
                                pad[side] = int(w.value)
                            except ValueError:
                                pad[side] = 0
                        self.set_value(option, pad)
            except Exception:
                pass
        return self.settings
