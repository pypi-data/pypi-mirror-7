import jinja2

from spec2scl import transformer


class Convertor(object):

    def __init__(self, spec, options=None):
        spec = self.list_to_str(spec)
        self.original_spec = spec
        self.options = options or {}

    def list_to_str(self, arg):
        if not isinstance(arg, str):
            arg = ''.join(arg)
        return arg

    def convert(self):
        if self.options['meta_spec']:
            return self.meta_convert()
        else:
            return transformer.Transformer(self.options).transform(self.original_spec)

    def meta_convert(self):
        data = transformer.MetaTransformer(self.original_spec, self.options['variables'])
        jinja_env = jinja2.Environment(loader=jinja2.ChoiceLoader([
            jinja2.FileSystemLoader(['/']),
            jinja2.PackageLoader('spec2scl', 'templates'), ]))
        jinja_template = jinja_env.get_template('metapackage.spec')
        return jinja_template.render(data=data)
