$("button.rowadd").click(function (evt) {
   /* Do not submit the form really */
   evt.preventDefault();
   /* Add first .form-field after last .form-field... */
   $(".variable-form:last").after(
       $(".variable-form:first").clone().hide().fadeIn());
});
