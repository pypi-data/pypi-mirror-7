from django.utils.translation import ugettext_lazy as _
from django.template import loader

from djangocms_text_ckeditor.cms_plugins import TextPlugin
from cms.plugin_pool import plugin_pool

class AjaxTextPlugin(TextPlugin):
    name = _(u'Text (asynchronous loading)')
    ajax_render_template = 'cms_ajax_text_plugin/plugin.html'

    def get_ajax_body(self, instance, context):
        t = loader.get_template(self.ajax_render_template)
        return t.render(context)

    def render(self, context, instance, placeholder):
        request = context.get('request')
        context['instance'] = instance
        if 'updatecache' in request.GET:
            instance.args = '?updatecache'
        edit_mode = request and 'edit' in request.GET
        is_ajax = request and request.is_ajax()
        if edit_mode or is_ajax:
            context = super(AjaxTextPlugin, self).render(context, instance, placeholder)
            return context

        context['body'] = self.get_ajax_body(instance, context)
        return context



plugin_pool.register_plugin(AjaxTextPlugin)
