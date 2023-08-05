from deform.widget import MappingWidget, SequenceWidget, Widget
import colander


class IPPDisplayWidget(Widget):
    def serialize(self, field, cstruct=None, readonly=False):
        return 'DISPLAY {}'.format(field.name.replace('_', '-'))


class IPPNameWidget(Widget):
    def serialize(self, field, cstruct=None, readonly=False):
        name = field.name
        while field.parent is not None:
            field = field.parent
        value = getattr(field.schema, name)
        return '{} "{}"'.format(name.upper(), value)


class IPPFileWidget(Widget):
    def serialize(self, field, cstruct=None, readonly=False):
        if cstruct is colander.null:
            return ''
        if not isinstance(cstruct, basestring):
            raise ValueError('Wrong value provided for field {!r}'.format(
                field.name))
        return 'FILE {}'.format(cstruct)


class IPPAttributeWidget(Widget):
    def serialize(self, field, cstruct=None, readonly=False):
        if cstruct is colander.null:
            return ''
        if cstruct is None:
            raise ValueError('None value provided for {!r}'.format(field.name))
        attr_name = field.schema.typ.__class__.__name__
        attr_name = attr_name[0].lower() + attr_name[1:]
        return 'ATTR {attr_type} {attr_name} {attr_value}'.format(
            attr_type=attr_name,
            attr_name=field.name.replace('_', '-'),
            attr_value=cstruct)


class IPPBodyWidget(MappingWidget):
    readonly_template = 'ipp/form'
    template = readonly_template
    item_template = 'ipp/item'


class IPPGroupWidget(SequenceWidget):
    readonly_template = 'ipp/group_tuple'
    template = readonly_template
    item_template = 'ipp/item'


class IPPConstantTupleWidget(SequenceWidget):
    readonly_template = 'ipp/constant_tuple'
    template = readonly_template
    item_template = 'ipp/item'
