"use strict";

// Class definition
var KTFormValidation = function () {
	// Elements
	var form;
	var formSubmitButton;
	var isSubmitButton;
	// Variables
	var validations = [];

	var initValidation = function (fieldsToValidate, isSubmit) {
		// Init form validation rules. For more info check the FormValidation plugin's official documentation:https://formvalidation.io/
		// Step 1
		validations.push(FormValidation.formValidation(
			form,
			{
				fields: fieldsToValidate,
				plugins: {
					trigger: new FormValidation.plugins.Trigger(),
					bootstrap: new FormValidation.plugins.Bootstrap5({
						rowSelector: '.fv-row',
                        eleInvalidClass: '',
                        eleValidClass: ''
					})
				}
			}
		));

		formSubmitButton.addEventListener('click', function (e) {
			// Validate form before change stepper step
			var validator = validations[0]; // get validator for last form

			validator.validate().then(function (status) {
				if (status == 'Valid') {
					// Prevent default button action
					e.preventDefault();

					// Disable button to avoid multiple click
					formSubmitButton.disabled = true;

					// Show loading indication
					formSubmitButton.setAttribute('data-kt-indicator', 'on');
					if (isSubmit) {
						form.submit();
					}else{
						// Simulate form submission
						setTimeout(function() {
							// Hide loading indication
							formSubmitButton.removeAttribute('data-kt-indicator');

							// Enable button
							formSubmitButton.disabled = false;
						}, 2000);
					}

				}
			});
		});
	}

	return {
		// Public Functions
		init: function (formID, formButton, fieldsToValidate, isSubmit=true) {
			form = document.querySelector(formID);
			formSubmitButton = document.querySelector(formButton);
			initValidation(fieldsToValidate, isSubmit);
		}
	};
}();
