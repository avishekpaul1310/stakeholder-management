# stakeholders/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Stakeholder
from .forms import StakeholderForm

class StakeholderListView(ListView):
    model = Stakeholder
    template_name = 'stakeholders/stakeholder_list.html'
    context_object_name = 'stakeholders'
    ordering = ['-created_at']

class StakeholderCreateView(CreateView):
    model = Stakeholder
    form_class = StakeholderForm
    template_name = 'stakeholders/stakeholder_form.html'
    success_url = reverse_lazy('stakeholder-list')

    def form_valid(self, form):
        messages.success(self.request, 'Stakeholder created successfully!')
        return super().form_valid(form)

class StakeholderUpdateView(UpdateView):
    model = Stakeholder
    form_class = StakeholderForm
    template_name = 'stakeholders/stakeholder_form.html'
    success_url = reverse_lazy('stakeholder-list')

    def form_valid(self, form):
        messages.success(self.request, 'Stakeholder updated successfully!')
        return super().form_valid(form)

class StakeholderDeleteView(DeleteView):
    model = Stakeholder
    template_name = 'stakeholders/stakeholder_confirm_delete.html'
    success_url = reverse_lazy('stakeholder-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Stakeholder deleted successfully!')
        return super().delete(request, *args, **kwargs)