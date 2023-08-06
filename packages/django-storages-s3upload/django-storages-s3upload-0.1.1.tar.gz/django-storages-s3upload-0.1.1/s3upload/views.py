# -*- coding: utf-8 -*-
#
# Copyright 2014 Matt Austin
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import absolute_import, unicode_literals
from . import settings
from .forms import DropzoneS3UploadForm, S3UploadForm, ValidateS3UploadForm
from django.core.files.storage import default_storage
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie


class S3UploadFormView(generic.edit.FormMixin,
                       generic.base.TemplateResponseMixin, generic.View):

    # TODO: Set additional metadata for upload, e.g. cache?

    content_type_prefix = ''  # e.g. 'image/', 'text/'

    form_class = S3UploadForm

    set_content_type = settings.SET_CONTENT_TYPE

    storage = default_storage

    template_name = 's3upload/form.html'

    upload_to = ''  # e.g. 'foo/bar/'

    def form_invalid(self, form):
        return HttpResponseBadRequest('Upload does not validate.')

    def form_valid(self, form, *args, **kwargs):
        if self.request.is_ajax():
            return HttpResponse()
        else:
            return super(S3UploadFormView, self).form_valid(form, *args,
                                                            **kwargs)

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        # If 'key' is in GET params, we're dealing with a new upload
        # (S3 redirect)
        if 'key' in request.GET:
            return self.validate_upload()

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))

    def get_content_type_prefix(self):
        return self.content_type_prefix

    def get_upload_to(self):
        return self.upload_to

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super(S3UploadFormView, self).get_form_kwargs(*args,
                                                                    **kwargs)
        form_kwargs.update(
            {'storage': self.get_storage(), 'upload_to': self.get_upload_to(),
             'content_type_prefix': self.get_content_type_prefix(),
             'success_action_redirect': self.get_success_action_redirect()})
        return form_kwargs

    def get_storage(self):
        return self.storage

    def get_success_action_redirect(self):
        return self.request.build_absolute_uri()

    @method_decorator(csrf_protect)
    def post(self, *args, **kwargs):
        return self.validate_upload()

    def validate_upload(self):
        # Validate a new upload
        data = {'bucket_name': self.request.REQUEST.get('bucket'),
                'key_name': self.request.REQUEST.get('key'),
                'etag': self.request.REQUEST.get('etag')}
        form = ValidateS3UploadForm(
            data=data, storage=self.get_storage(),
            content_type_prefix=self.get_content_type_prefix(),
            upload_to=self.get_upload_to())
        if form.is_valid():
            if self.set_content_type:
                form.set_content_type()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class DropzoneS3UploadFormView(S3UploadFormView):

    form_class = DropzoneS3UploadForm

    template_name = 's3upload/dropzone_form.html'

    def get_success_action_redirect(self):
        return None
