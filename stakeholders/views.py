from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Stakeholder
from .forms import StakeholderForm

class StakeholderListView(ListView):
    model = Stakeholder
    template_name = 'stakeholders/stakeholder_list.html'
    context_object_name = 'stakeholders'

class StakeholderCreateView(CreateView):
    model = Stakeholder
    form_class = StakeholderForm
    template_name = 'stakeholders/stakeholder_form.html'
    success_url = reverse_lazy('stakeholder-list')

class StakeholderUpdateView(UpdateView):
    model = Stakeholder
    form_class = StakeholderForm
    template_name = 'stakeholders/stakeholder_form.html'
    success_url = reverse_lazy('stakeholder-list')

class StakeholderDeleteView(DeleteView):
    model = Stakeholder
    template_name = 'stakeholders/stakeholder_confirm_delete.html'
    success_url = reverse_lazy('stakeholder-list')