from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic 
from feedback.forms import FeedbackForm



class FeedbackFormView(LoginRequiredMixin, generic.FormView):
    form_class = FeedbackForm 
    template_name = "feedback/feedback_form.html"

    def form_valid(self, form):
        feedback = form.save(commit=False)
        feedback.user = self.request.user 
        feedback.save() 
        return render(self.request, "feedback/thanks.html")