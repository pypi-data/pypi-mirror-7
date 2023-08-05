from braces.views import StaffuserRequiredMixin, LoginRequiredMixin, OrderableListMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView, UpdateView
from django.http import HttpResponseRedirect
from django.contrib import messages
from realestate.home.models import Contact
from realestate.listing.models import Listing, Agent, City, Sector
from realestate.admin.forms import ListingForm, ListingImageFormSet, AttributeListingFormSet

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}


class Dashboard(LoginRequiredMixin, StaffuserRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'


class CreateListing(LoginRequiredMixin, StaffuserRequiredMixin, CreateView):
    template_name = 'dashboard/create-listing.html'
    model = Listing
    form_class = ListingForm
    success_url = reverse_lazy('admin-list-listing')

    def get_context_data(self, **kwargs):
        context = super(CreateListing, self).get_context_data(**kwargs)
        if self.request.POST:
            context['listing_images_form'] = ListingImageFormSet(self.request.POST, self.request.FILES)
            context['listing_attributes_form'] = AttributeListingFormSet(self.request.POST, self.request.FILES)
        else:
            context['listing_images_form'] = ListingImageFormSet()
            context['listing_attributes_form'] = AttributeListingFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        listing_images_form = context['listing_images_form']
        listing_attributes_form = context['listing_attributes_form']

        if listing_images_form.is_valid() and form.is_valid() and listing_attributes_form.is_valid():
            self.object = form.save()  # saves Father and Children
            listing_images_form.instance = self.object
            listing_images_form.save()
            listing_attributes_form.instance = self.object
            listing_attributes_form.save()

            messages.success(self.request, 'Listing created successfully.')

            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class UpdateListing(LoginRequiredMixin, StaffuserRequiredMixin, UpdateView):
    template_name = 'dashboard/create-listing.html'
    model = Listing
    form_class = ListingForm
    success_url = reverse_lazy('admin-list-listing')

    def get_context_data(self, **kwargs):
        context = super(UpdateListing, self).get_context_data(**kwargs)
        if self.request.POST:
            context['listing_images_form'] = ListingImageFormSet(self.request.POST, self.request.FILES,
                                                                 instance=self.object)
            context['listing_attributes_form'] = AttributeListingFormSet(self.request.POST, self.request.FILES,
                                                                         instance=self.object)
        else:
            context['listing_images_form'] = ListingImageFormSet(instance=self.object)
            context['listing_attributes_form'] = AttributeListingFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        listing_images_form = context['listing_images_form']
        listing_attributes_form = context['listing_attributes_form']

        if listing_images_form.is_valid() and form.is_valid() and listing_attributes_form.is_valid():
            form.save()  # saves Father and Children
            listing_images_form.save()
            listing_attributes_form.save()

            messages.success(self.request, 'Listing updated successfully.')

            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class Listings(LoginRequiredMixin, StaffuserRequiredMixin, ListView):
    template_name = 'dashboard/listings.html'
    model = Listing


class Agents(LoginRequiredMixin, StaffuserRequiredMixin, OrderableListMixin, ListView):
    template_name = 'dashboard/agents.html'
    model = Agent
    orderable_columns = ('id', 'name',)
    orderable_columns_default = 'id'


class CreateAgent(LoginRequiredMixin, StaffuserRequiredMixin, CreateView):
    template_name = 'dashboard/create-agent.html'
    model = Agent
    success_url = reverse_lazy('admin-list-agents')


class UpdateAgent(LoginRequiredMixin, StaffuserRequiredMixin, UpdateView):
    template_name = 'dashboard/create-agent.html'
    model = Agent
    success_url = reverse_lazy('admin-list-agents')


class Contacts(LoginRequiredMixin, StaffuserRequiredMixin, OrderableListMixin, ListView):
    template_name = 'dashboard/contacts.html'
    model = Contact
    orderable_columns = ('id', 'name',)
    orderable_columns_default = 'id'


class CreateContact(LoginRequiredMixin, StaffuserRequiredMixin, CreateView):
    template_name = 'dashboard/create-contact.html'
    model = Contact
    success_url = reverse_lazy('admin-list-contacts')


class UpdateContact(LoginRequiredMixin, StaffuserRequiredMixin, UpdateView):
    template_name = 'dashboard/create-contact.html'
    model = Contact
    success_url = reverse_lazy('admin-list-contacts')


class Cities(LoginRequiredMixin, StaffuserRequiredMixin, OrderableListMixin, ListView):
    template_name = 'dashboard/cities.html'
    model = City
    orderable_columns = ('id', 'name',)
    orderable_columns_default = 'id'


class CreateCity(LoginRequiredMixin, StaffuserRequiredMixin, CreateView):
    template_name = 'dashboard/create-city.html'
    model = City
    success_url = reverse_lazy('admin-list-cities')


class UpdateCity(LoginRequiredMixin, StaffuserRequiredMixin, UpdateView):
    template_name = 'dashboard/create-city.html'
    model = City
    success_url = reverse_lazy('admin-list-cities')


class Sectors(LoginRequiredMixin, StaffuserRequiredMixin, OrderableListMixin, ListView):
    template_name = 'dashboard/sectors.html'
    model = Sector
    orderable_columns = ('id', 'name',)
    orderable_columns_default = 'id'


class CreateSector(LoginRequiredMixin, StaffuserRequiredMixin, CreateView):
    template_name = 'dashboard/create-sector.html'
    model = Sector
    success_url = reverse_lazy('admin-list-sectors')


class UpdateSector(LoginRequiredMixin, StaffuserRequiredMixin, UpdateView):
    template_name = 'dashboard/create-sector.html'
    model = Sector
    success_url = reverse_lazy('admin-list-sectors')
