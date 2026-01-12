# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

import warnings
from enum import EnumMeta


class DeprecationEnumMeta(EnumMeta):
    """Enum metaclass that emits a deprecation warning when a member is accessed.

    Accessing a member like `BushingConfig.SINGLE_BUSHING` will trigger the
    warning so users see the deprecation at the point of use.
    """

    def __getattribute__(cls, name: str) -> object:
        """This method is called when an attribute is accessed on the class.

        Access the class __dict__ via object.__getattribute__ to avoid
        invoking this metaclass's __getattribute__ again which would
        cause recursion during class creation.

        Args:
            name (str): attribute name being accessed.

        Returns:
            object: The attribute value.
        """
        val = super().__getattribute__(name)
        member_map = object.__getattribute__(cls, "__dict__").get("_member_map_", {})
        if name in member_map:
            warnings.warn(
                f"{super().__name__} was deprecated in version v0.4.0 and will be removed in v1.0.0.",
                category=DeprecationWarning,
                stacklevel=3,
            )
        return val
