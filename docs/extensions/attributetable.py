from __future__ import annotations

import importlib
import inspect
import re
from collections.abc import Sequence
from typing import NamedTuple

from docutils import nodes
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.locale import _ as translate
from sphinx.util.docutils import SphinxDirective
from sphinx.util.typing import OptionSpec
from sphinx.writers.html5 import HTML5Translator


class AttributeTable(nodes.General, nodes.Element):
    pass


class AttributeTableColumn(nodes.General, nodes.Element):
    pass


class AttributeTableTitle(nodes.TextElement):
    pass


class AttributeTablePlaceholder(nodes.General, nodes.Element):
    pass


class AttributeTableBadge(nodes.TextElement):
    pass


class AttributeTableItem(nodes.Part, nodes.Element):
    pass


def visit_attributetable_node(self: HTML5Translator, node: AttributeTable) -> None:
    class_ = node["python-class"]
    self.body.append(f'<div class="py-attribute-table" data-move-to-id="{class_}">')


def visit_attributetablecolumn_node(self: HTML5Translator, node: AttributeTableColumn) -> None:
    self.body.append(self.starttag(node, "div", CLASS="py-attribute-table-column"))


def visit_attributetabletitle_node(self: HTML5Translator, node: AttributeTableTitle) -> None:
    self.body.append(self.starttag(node, "span"))


def visit_attributetablebadge_node(self: HTML5Translator, node: AttributeTableBadge) -> None:
    attributes = {
        "class": "py-attribute-table-badge",
        "title": node["badge-type"],
    }
    self.body.append(self.starttag(node, "span", **attributes))


def visit_attributetable_item_node(self: HTML5Translator, node: AttributeTableItem) -> None:
    self.body.append(self.starttag(node, "li", CLASS="py-attribute-table-entry"))


def depart_attributetable_node(self: HTML5Translator, node: AttributeTable) -> None:
    self.body.append("</div>")


def depart_attributetablecolumn_node(self: HTML5Translator, node: AttributeTableColumn) -> None:
    self.body.append("</div>")


def depart_attributetabletitle_node(self: HTML5Translator, node: AttributeTableTitle) -> None:
    self.body.append("</span>")


def depart_attributetablebadge_node(self: HTML5Translator, node: AttributeTableBadge) -> None:
    self.body.append("</span>")


def depart_attributetable_item_node(self: HTML5Translator, node: AttributeTableItem) -> None:
    self.body.append("</li>")


_name_parser_regex = re.compile(r"(?P<module>[\w.]+\.)?(?P<name>\w+)")


class PyAttributeTable(SphinxDirective):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec: OptionSpec = {}  # noqa: RUF012 # (from original impl)

    def parse_name(self, content: str) -> tuple[str, str]:
        match = _name_parser_regex.match(content)
        if match is None:
            raise RuntimeError(f"content {content} somehow doesn't match regex in {self.env.docname}.")
        path, name = match.groups()
        if path:
            modulename = path.rstrip(".")
        else:
            modulename = self.env.temp_data.get("autodoc:module")
            if not modulename:
                modulename = self.env.ref_context.get("py:module")
        if modulename is None:
            raise RuntimeError(f"modulename somehow None for {content} in {self.env.docname}.")

        return modulename, name

    def run(self) -> list[AttributeTablePlaceholder]:
        """If you're curious on the HTML this is meant to generate:

        <div class="py-attribute-table">
            <div class="py-attribute-table-column">
                <span>translate('Attributes')</span>
                <ul>
                    <li>
                        <a href="...">
                    </li>
                </ul>
            </div>
            <div class="py-attribute-table-column">
                <span>translate('Methods')</span>
                <ul>
                    <li>
                        <a href="..."></a>
                        <span class="py-attribute-badge" title="decorator">D</span>
                    </li>
                </ul>
            </div>
        </div>

        However, since this requires the tree to be complete
        and parsed, it'll need to be done at a different stage and then
        replaced.
        """
        content = self.arguments[0].strip()
        node = AttributeTablePlaceholder("")
        modulename, name = self.parse_name(content)
        node["python-doc"] = self.env.docname
        node["python-module"] = modulename
        node["python-class"] = name
        node["python-full-name"] = f"{modulename}.{name}"
        return [node]


def build_lookup_table(env: BuildEnvironment) -> dict[str, list[str]]:
    # Given an environment, load up a lookup table of
    # full-class-name: objects
    result = {}
    domain = env.domains["py"]

    ignored = {
        "data",
        "exception",
        "module",
        "class",
    }

    for fullname, _, objtype, _, _, _ in domain.get_objects():
        if objtype in ignored:
            continue

        classname, _, child = fullname.rpartition(".")
        try:
            result[classname].append(child)
        except KeyError:
            result[classname] = [child]

    return result


class TableElement(NamedTuple):
    fullname: str
    label: str
    badge: AttributeTableBadge | None


def process_attributetable(app: Sphinx, doctree: nodes.Node, fromdocname: str) -> None:
    env = app.builder.env

    lookup = build_lookup_table(env)
    for node in doctree.traverse(AttributeTablePlaceholder):
        modulename, classname, fullname = node["python-module"], node["python-class"], node["python-full-name"]
        groups = get_class_results(lookup, modulename, classname, fullname)
        table = AttributeTable("")
        for label, subitems in groups.items():
            if not subitems:
                continue
            table.append(class_results_to_node(label, sorted(subitems, key=lambda c: c.label)))

        table["python-class"] = fullname

        if not table:
            node.replace_self([])
        else:
            node.replace_self([table])


def get_class_results(
    lookup: dict[str, list[str]], modulename: str, name: str, fullname: str
) -> dict[str, list[TableElement]]:
    module = importlib.import_module(modulename)
    cls = getattr(module, name)

    groups: dict[str, list[TableElement]] = {
        translate("Attributes"): [],
        translate("Methods"): [],
    }

    try:
        members = lookup[fullname]
    except KeyError:
        return groups

    for attr in members:
        attrlookup = f"{fullname}.{attr}"
        key = translate("Attributes")
        badge = None
        label = attr
        value = None

        for base in cls.__mro__:
            value = base.__dict__.get(attr)
            if value is not None:
                break

        if value is not None:
            doc = value.__doc__ or ""
            if inspect.iscoroutinefunction(value) or doc.startswith("|coro|"):
                key = translate("Methods")
                badge = AttributeTableBadge("async", "async")
                badge["badge-type"] = translate("coroutine")
            elif isinstance(value, classmethod):
                key = translate("Methods")
                label = f"{name}.{attr}"
                badge = AttributeTableBadge("cls", "cls")
                badge["badge-type"] = translate("classmethod")
            elif inspect.isfunction(value):
                if doc.startswith(("A decorator", "A shortcut decorator")):
                    # finicky but surprisingly consistent
                    key = translate("Methods")
                    badge = AttributeTableBadge("@", "@")
                    badge["badge-type"] = translate("decorator")
                elif inspect.isasyncgenfunction(value):
                    key = translate("Methods")
                    badge = AttributeTableBadge("async for", "async for")
                    badge["badge-type"] = translate("async iterable")
                else:
                    key = translate("Methods")
                    badge = AttributeTableBadge("def", "def")
                    badge["badge-type"] = translate("method")

        groups[key].append(TableElement(fullname=attrlookup, label=label, badge=badge))

    return groups


def class_results_to_node(key: str, elements: Sequence[TableElement]) -> AttributeTableColumn:
    title = AttributeTableTitle(key, key)
    ul = nodes.bullet_list("")
    for element in elements:
        ref = nodes.reference(
            "",
            "",
            internal=True,
            refuri=f"#{element.fullname}",
            anchorname="",
            *[nodes.Text(element.label)],  # noqa: B026 # (from original impl)
        )
        para = addnodes.compact_paragraph("", "", ref)
        if element.badge is not None:
            ul.append(AttributeTableItem("", element.badge, para))
        else:
            ul.append(AttributeTableItem("", para))

    return AttributeTableColumn("", title, ul)


def setup(app: Sphinx) -> dict:
    app.add_directive("attributetable", PyAttributeTable)
    app.add_node(AttributeTable, html=(visit_attributetable_node, depart_attributetable_node))
    app.add_node(AttributeTableColumn, html=(visit_attributetablecolumn_node, depart_attributetablecolumn_node))
    app.add_node(AttributeTableTitle, html=(visit_attributetabletitle_node, depart_attributetabletitle_node))
    app.add_node(AttributeTableBadge, html=(visit_attributetablebadge_node, depart_attributetablebadge_node))
    app.add_node(AttributeTableItem, html=(visit_attributetable_item_node, depart_attributetable_item_node))
    app.add_node(AttributeTablePlaceholder)
    app.connect("doctree-resolved", process_attributetable)
    return {"parallel_read_safe": True}
