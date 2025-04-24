import os
import sys
from tkinter.font import names

if sys.platform == "win32":
    os.system("")


# === custom Exceptions ===

class ColourFormatError(Exception):
    """
    Raised when an unsupported type is passed to a Colour formatter.
    """
    pass


class ListIndexOutOfRange(Exception):
    """
    Raised when a provided index is outside the bounds of a list or tuple.
    """
    pass


class DictKeyMissing(Exception):
    """
    Raised when a specified key is not found in the dictionary being styled.
    """
    pass


class DictValueMissing(Exception):
    """
    Raised when a specified value is not found in the dictionary being styled.
    """
    pass


# === Detailed Usage Examples ===
USAGE_DETAIL_TEXT = r"""
# 1. Single-value styling

print(Colour.RED("Error"))        # “Error” in red
print(Colour.GREEN("✔ Success"))  # green checkmark + text
print(Colour.YELLOW(123))           # “123” in yellow
print(Colour.CYAN(3.14))            # “3.14” in cyan
print(Colour.MAGENTA(True))         # “True” in magenta
print(Colour.BLUE(None))            # “None” in blue

# 2. ListFormatter (.LIST)

fruits = ["apple","banana","cherry"]
print(Colour.GREEN.LIST(fruits))
print(Colour.RED.LIST(fruits, indices=[0,2]))

# 3. TupleFormatter (.TUPLE)

coords = ("x","y","z")
print(Colour.BLUE.TUPLE(coords))
print(Colour.YELLOW.TUPLE(coords, indices=[1]))

# 4. DictFormatter (.DICT)

data = {"name":"Alice","city":"Paris","age":"30"}
print(Colour.RED.DICT(data))                               # all values
print(Colour.GREEN.DICT(data, target="key"))             # all keys
print(Colour.MAGENTA.DICT(data, target="both"))          # keys & values
print(Colour.CYAN.DICT(data, keys=["city"], target="value"))
print(Colour.YELLOW.DICT(data, values=["30"], target="value"))
print(Colour.BLUE.DICT(data, keys=["name"], values=["Alice"], target="both"))

# 5. RandomFormatter (.RANDOMISE)

print(Colour.RANDOMISE("Randomly colored!"))
print(Colour.RANDOMISE.LIST(["a","b","c"], indices=[1]))
print(Colour.RANDOMISE.TUPLE(("x","y","z"), indices=[2]))
print(Colour.RANDOMISE.DICT(data, target="value", keys=["city"]))

# 6. TargetFormatter (.TARGET)

text = "Aa, Bb, Cc 755 667"
print(Colour.YELLOW.TARGET("A","B","7","5")(text))
print(Colour.CYAN.TARGET("a")("AaAa"))
print(Colour.RED.TARGET("1")([1,2,11]))
"""

# === Colour Enum ===


from enum import Enum, member
from typing import Union
import random


class Colour(Enum):
    """
    Custom colour/styling enum-based module.
    Provides ANSI-based foreground/background colours, text styles, and formatters.
    For live demonstration, refer to ColourDemo.
    """

    # foreground Colours
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    MAGENTA = '\033[35m'
    WHITE = '\033[37m'
    BLACK = '\033[30m'
    LIGHTRED = '\033[91m'
    LIGHTGREEN = '\033[92m'
    LIGHTYELLOW = '\033[93m'
    LIGHTBLUE = '\033[94m'
    LIGHTMAGENTA = '\033[95m'
    LIGHTCYAN = '\033[96m'
    GREY = '\033[90m'

    # background colours
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_CYAN = '\033[46m'
    BG_MAGENTA = '\033[45m'
    BG_WHITE = '\033[47m'
    BG_BLACK = '\033[40m'
    BG_LIGHTRED = '\033[101m'
    BG_LIGHTGREEN = '\033[102m'
    BG_LIGHTYELLOW = '\033[103m'
    BG_LIGHTBLUE = '\033[104m'
    BG_LIGHTMAGENTA = '\033[105m'
    BG_LIGHTCYAN = '\033[106m'
    BG_GREY = '\033[100m'

    # style Modifiers
    BRIGHT = '\033[1m'
    DIM = '\033[2m'
    NORMAL = '\033[22m'
    RESET = '\033[0m'

    def __call__(self, text: Union[str, int, float, bool, None]) -> str:
        """
        Apply this colour/style to the given text.
        Automatically resets formatting after application.
        """
        if not isinstance(text, (str, int, float, bool, type(None))):
            raise ColourFormatError(f"Unsupported type: {type(text).__name__}")
        return f"{self.value}{str(text)}{Colour.RESET.value}"

    @classmethod
    def get_supported_colours(cls, mode: Union[str, 'name', 'member',]) -> list:
        """
        Return supported colour enum members based on the mode:
        - 'name': returns a list of names                    = ['RED', 'GREEN',...]
        - 'member': returns a list of Colour enum instances  = [Colour.RED, Colour.GREEN,...]
        """
        skip = {'BRIGHT', 'DIM', 'NORMAL', 'RESET', 'RANDOMISE'}
        if mode == 'member':
            return [member for name, member in cls.__members__.items() if name not in skip]

        elif mode == 'name':
            return [name for name in cls.__members__ if name not in skip]

        else:
            raise ValueError(f"Invalid mode: {mode}")

    def styled(self, text: str, *others: 'Colour') -> str:
        """
        Apply this colour and any additional Colour styles to the given text.
        Returns the styled string with an ANSI reset at the end.
        """
        codes = ''.join(member.value for member in (self, *others))
        return f"{codes}{text}{Colour.RESET.value}"

    @property
    def LIST(self):
        return Colour._ListFormatter(self)

    @property
    def TUPLE(self):
        return Colour._TupleFormatter(self)

    @property
    def DICT(self):
        return Colour._DictFormatter(self)

    @property
    def RANDOM(self):
        return Colour._RandomFormatter()

    def TARGET(self, *args):
        return Colour._TargetFormatter(self, args)

    @staticmethod
    def USAGE_DETAIL() -> str:
        return print(USAGE_DETAIL_TEXT)


    class _TargetFormatter:
        def __init__(self, colour, targets):
            self.colour = colour
            self.targets = set(str(t) for t in targets)

        def __call__(self, text):
            return ''.join(
                f"{self.colour.value}{c}{Colour.RESET.value}" if c in self.targets else c
                for c in str(text)
            )

    class _ListFormatter:
        def __init__(self, colour):
            self.colour = colour

        def __call__(self, items, indices=None):
            if not all(isinstance(i, str) for i in items):
                raise ColourFormatError("All list items must be strings.")
            if indices is None:
                return [self.colour(i) for i in items]
            for idx in indices:
                if idx < 0 or idx >= len(items):
                    raise ListIndexOutOfRange(f"Index {idx} out of range.")
            return [self.colour(i) if idx in indices else i for idx, i in enumerate(items)]

    class _TupleFormatter:
        def __init__(self, colour):
            self.colour = colour

        def __call__(self, items, indices=None):
            if not all(isinstance(i, str) for i in items):
                raise ColourFormatError("All tuple items must be strings.")
            if indices is None:
                return tuple(self.colour(i) for i in items)
            for idx in indices:
                if idx < 0 or idx >= len(items):
                    raise ListIndexOutOfRange(f"Index {idx} out of range.")
            return tuple(self.colour(i) if idx in indices else i for idx, i in enumerate(items))

    class _DictFormatter:
        def __init__(self, colour):
            self.colour = colour

        def __call__(self, items, keys=None, values=None, target="value"):
            if not all(isinstance(k, str) for k in items):
                raise ColourFormatError("All keys must be strings.")
            if target not in ("key", "value", "both"):
                raise ColourFormatError("Target must be 'key','value', or 'both'.")
            if keys:
                for k in keys:
                    if k not in items:
                        raise DictKeyMissing(f"Key '{k}' missing.")
            if values:
                for v in values:
                    if v not in items.values():
                        raise DictValueMissing(f"Value '{v}' missing.")
            out = {}
            for k, v in items.items():
                k_ok = keys is None or k in keys
                v_ok = values is None or v in values
                if target == "key":
                    out[self.colour(k) if k_ok else k] = v
                elif target == "value":
                    out[k] = self.colour(v) if v_ok else v
                else:
                    out[self.colour(k) if k_ok else k] = self.colour(v) if v_ok else v
            return out

        class _RandomFormatter:
            def __init__(self, Colour):
                self.colour = Colour

            @property
            def _pool(self):
                return Colour.get_supported_colours('member')

            def pick(self, pool=None):
                return random.choice(pool or self._pool)

            def SINGLE(self, v, c=None):
                return self.pick(c)(v)

            def LIST(self, items, indices=None, c=None):
                return self.pick(c).LIST(items, indices)

            def TUPLE(self, items, indices=None, c=None):
                return self.pick(c).TUPLE(items, indices)

            def DICT(self, items, keys=None, values=None, target="value", c=None):
                return self.pick(c).DICT(items, keys, values, target)

            def RANDOM(self, v, c=None):
                return self.pick(c)(v)

            def __call__(self, v, c=None):
                return self.SINGLE(v, c)

            def __repr__(self):
                return ""

    class _RandomiseFormater:
        def __init__(self, colour):
            self.colour = colour
        pass
# ============================================DEMO========================================================#
class ColourDemo:
    """
    Simple Demo of Colour usage
    for all demos -> call: all_formatters_demo()

    # """

    @staticmethod
    def supported_colours():
        names = Colour.get_supported_colours("name")
        members = Colour.get_supported_colours("member")

        for name, member in zip(names, members):
            print(f"{member.value}{name}:{Colour.RESET.value}")



    @staticmethod
    def single_value_styling():
        print(f"\n{Colour.GREEN.styled('# 1. Single-value styling', Colour.BRIGHT)}")
        print()
        print(Colour.MAGENTA.styled("Colour individual values", Colour.BRIGHT))
        print(f"{ColourDemo._get_example_prefix()} print(Colour.RED(\"Error\")")
        print(f"{ColourDemo._get_example_prefix()} print(Colour.GREEN(\""f"Success\")")
        print("...")
        print(Colour.RED("Error"), "→ RED on string")
        print(Colour.GREEN("Success"), "→ GREEN on checkmark")
        print(Colour.YELLOW(123), "→ YELLOW on int")
        print(Colour.CYAN(3.14), "→ CYAN on float")
        print(Colour.MAGENTA(True), "→ MAGENTA on bool")
        print(Colour.BLUE(None), "→ BLUE on None")
        print(f"Error type -> {type("Error")}")
        print(f"Success type -> {type('Success')}")
        print(f"123 type -> {type(123)}")
        print(f"3.14 type -> {type(3.14)}")
        print(f"True type -> {type(True)}")
        print(f"None type -> {type(None)}")

        ColourDemo._separator()

    @staticmethod
    def list_formatter_demo():
        print(f"\n{Colour.GREEN.styled('# 2. ListFormatter (.LIST)', Colour.BRIGHT)}")
        fruits = ["apple", "banana", "cherry"]
        print("Original:", fruits)
        print()
        print(Colour.MAGENTA.styled("Colour entire or partial list", Colour.BRIGHT))
        print(f"{ColourDemo._get_example_prefix()} 'print(\"All coloured:\", Colour.GREEN.LIST(fruits))'")
        all_coloured = Colour.GREEN.LIST(fruits)
        ColourDemo._show_ansi(all_coloured)
        print()

        print()
        print(Colour.MAGENTA.styled("Colour index 0 and 2 only", Colour.BRIGHT))
        print(f"{ColourDemo._get_example_prefix()} 'print(\"Indices [0,2]:\", Colour.RED.LIST(fruits, indices=[0,2]))'")
        some_coloured = Colour.RED.LIST(fruits, indices=[0, 2])
        ColourDemo._show_ansi(some_coloured)
        print()
        ColourDemo._separator()

    @staticmethod
    def tuple_formatter_demo():
        print(f"\n{Colour.GREEN.styled('# 3. TupleFormatter (.TUPLE)', Colour.BRIGHT)}")
        coords = ("x", "y", "z")
        print("Original:", coords)
        print()
        print(Colour.MAGENTA.styled("Colour ALL object in TUPLE", Colour.BRIGHT))
        print(f"{ColourDemo._get_example_prefix()} 'print(\"All coloured:\", Colour.BLUE.TUPLE(coords))'")
        all_coords = Colour.BLUE.TUPLE(coords)
        ColourDemo._show_ansi(all_coords)
        print()

        print()
        print(Colour.MAGENTA.styled("Colour object at index [1]", Colour.BRIGHT))
        print(f"{ColourDemo._get_example_prefix()} 'print(\"Index [1]:\", Colour.YELLOW.TUPLE(coords, indices=[1]))'")
        some_coords = Colour.YELLOW.TUPLE(coords, indices=[1])
        ColourDemo._show_ansi(some_coords)
        print()
        ColourDemo._separator()

    @staticmethod
    def dict_formatter_demo():
        print(f"\n{Colour.GREEN.styled('# 4. DictFormatter (.DICT)', Colour.BRIGHT)}")
        data = {"name": "Alice", "city": "Paris", "age": "30"}
        print("Original:", data)
        print()
        print(Colour.MAGENTA.styled("Colour values in dict", Colour.BRIGHT))
        print(f"{ColourDemo._get_example_prefix()} 'print(Colour.RED.DICT(data))'")
        val_dict = Colour.RED.DICT(data)
        ColourDemo._show_ansi(val_dict)
        print()

        print()
        print(Colour.MAGENTA.styled("Colour keys in dict", Colour.BRIGHT))
        print(f"{ColourDemo._get_example_prefix()} 'print(Colour.GREEN.DICT(data, target=\"key\"))'")
        key_dict = Colour.GREEN.DICT(data, target="key")
        ColourDemo._show_ansi(key_dict)
        print()

        print()
        print(Colour.MAGENTA.styled("Colour both keys and values", Colour.BRIGHT))
        print(
            f"{ColourDemo._get_example_prefix()} 'print(\"Both target:\", Colour.MAGENTA.DICT(data, target=\"both\"))'")
        both_dict = Colour.MAGENTA.DICT(data, target="both")
        ColourDemo._show_ansi(both_dict)
        print()

        print()
        print(Colour.MAGENTA.styled("Colour value of key 'city'", Colour.BRIGHT))
        print(
            f"{ColourDemo._get_example_prefix()} 'print(\"Value of city:\", Colour.CYAN.DICT(data, keys=[\"city\"], target=\"value\"))'")
        city_val = Colour.CYAN.DICT(data, keys=["city"], target="value")
        ColourDemo._show_ansi(city_val)
        print()

        print()
        print(Colour.MAGENTA.styled("Colour value '30'", Colour.BRIGHT))
        print(
            f"{ColourDemo._get_example_prefix()} 'print(\"Value \\\"30\\\":\", Colour.YELLOW.DICT(data, values=[\"30\"], target=\"value\"))'")
        age_val = Colour.YELLOW.DICT(data, values=["30"], target="value")
        ColourDemo._show_ansi(age_val)
        print()
        ColourDemo._separator()

    @staticmethod
    def random_formatter_demo():
        print(f"\n{Colour.GREEN.styled('# 5. RandomFormatter (.RANDOMISE)', Colour.BRIGHT)}")
        print()
        print(Colour.MAGENTA.styled("Random colour on single item", Colour.BRIGHT))
        print(
            f"{ColourDemo._get_example_prefix()} 'print(\"Random single:\", Colour.RANDOMISE(\"Randomly colored!\"))'")
        rand_single = Colour.RANDOMISE("Randomly colored!")
        ColourDemo._show_ansi(rand_single)
        print()

        print()
        print(Colour.MAGENTA.styled("Random colour on index 1 in list", Colour.BRIGHT))
        print(
            f"{ColourDemo._get_example_prefix()} 'print(\"Random list:\", Colour.RANDOMISE.LIST([\"a\", \"b\", \"c\"], indices=[1]))'")
        rand_list = Colour.RANDOMISE.LIST(["a", "b", "c"], indices=[1])
        ColourDemo._show_ansi(rand_list)
        print()

        print()
        print(Colour.MAGENTA.styled("Random colour on index 2 in tuple", Colour.BRIGHT))
        print(
            f"{ColourDemo._get_example_prefix()} 'print(\"Random tuple:\", Colour.RANDOMISE.TUPLE((\"x\", \"y\", \"z\"), indices=[2]))'")
        rand_tuple = Colour.RANDOMISE.TUPLE(("x", "y", "z"), indices=[2])
        ColourDemo._show_ansi(rand_tuple)
        print()

        print()
        print(Colour.MAGENTA.styled("Random colour for value of key 'city'", Colour.BRIGHT))
        print(
            f"{ColourDemo._get_example_prefix()} 'print(\"Random dict:\", Colour.RANDOMISE.DICT(data, target=\"value\", keys=[\"city\"]))'")
        rand_dict = Colour.RANDOMISE.DICT({"name": "Alice", "city": "Paris", "age": "30"}, target="value",
                                          keys=["city"])
        ColourDemo._show_ansi(rand_dict)
        print()
        ColourDemo._separator()

    @staticmethod
    def target_formatter_demo():
        print(f"\n{Colour.GREEN.styled('# 6. TargetFormatter (.TARGET)', Colour.BRIGHT)}")
        text = "Aa, Bb, Cc 755 667"

        print()
        print(Colour.MAGENTA.styled("Target and colour A, B, 7, 5", Colour.BRIGHT))
        print(
            f"{ColourDemo._get_example_prefix()} 'print(\"Targets A,B,7,5:\", Colour.YELLOW.TARGET(\"A\", \"B\", \"7\", \"5\")(text))'")
        ColourDemo._show_ansi(Colour.YELLOW.TARGET("A", "B", "7", "5")(text))
        print()

        print()
        print(Colour.MAGENTA.styled("Target and colour lowercase a", Colour.BRIGHT))
        print(f"{ColourDemo._get_example_prefix()} 'print(\"Target lowercase a:\", Colour.CYAN.TARGET(\"a\")(text))'")
        ColourDemo._show_ansi(Colour.CYAN.TARGET("a")(text))
        print()

        print()
        print(Colour.MAGENTA.styled("Target and colour digit 1", Colour.BRIGHT))
        print(f"{ColourDemo._get_example_prefix()} 'print(\"Target digit '1':\", Colour.RED.TARGET(\"1\")(text))'")
        ColourDemo._show_ansi(Colour.RED.TARGET("1")(text))
        print()
        ColourDemo._separator()

    @staticmethod
    def all_formatters_demo():
        ColourDemo.supported_colours()
        ColourDemo.single_value_styling()
        ColourDemo.list_formatter_demo()
        ColourDemo.tuple_formatter_demo()
        # ColourDemo.dict_formatter_demo()
        # ColourDemo.random_formatter_demo()
        # ColourDemo.target_formatter_demo()

    @staticmethod
    def _get_example_prefix():
        return Colour.CYAN.styled("EXAMPLE HOW TO CALL IT: ", Colour.BRIGHT)

    @staticmethod
    def _get_ansi_example():
        return Colour.MAGENTA.styled("ANSI Format: ", Colour.BRIGHT)

    @staticmethod
    def _separator():
        print(f"{Colour.BG_WHITE.styled(" " * 90, Colour.BRIGHT)}")

    @staticmethod
    def _show_ansi(value, max_width=80):
        styled_label = lambda text: Colour.YELLOW.styled(text, Colour.BRIGHT)
        print(f"{Colour.YELLOW.styled('ANSI REPRESENTATION', Colour.BRIGHT)}")

        def truncate_repr(s):
            raw = repr(s)
            return raw if len(raw) <= max_width else raw[:max_width - 3] + "..."

        if isinstance(value, (list, tuple)):
            print(f"{styled_label('FULL')} → {truncate_repr(value)}")
            print(f"{styled_label('ITEMS')}:")
            ansi_reprs = [truncate_repr(item) for item in value]
            width = max(len(s) for s in ansi_reprs) if ansi_reprs else 0
            for item, ansi in zip(value, ansi_reprs):
                print(f"{ansi.ljust(width)} → {item}")

        elif isinstance(value, dict):
            print(f"{styled_label('FULL')} → {truncate_repr(value)}")
            print(f"{styled_label('DICT ITEMS')}:")
            ansi_reprs = {k: truncate_repr(v) for k, v in value.items()}
            width = max(len(s) for s in ansi_reprs.values()) if ansi_reprs else 0
            for k, v in value.items():
                ansi = ansi_reprs[k]
                print(f"{ansi.ljust(width)} → {k}")

        else:
            print(f"{styled_label('SINGLE VALUE')} → {truncate_repr(value)}")



