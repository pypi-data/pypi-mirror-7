picker
======

Questa è una alternativa al widget standar di django

Dipendenze
----------

* jquery > 1.9
* jquery.ui > 1.10
* timepicker-addon e sliderAccess: http://trentrichardson.com/examples/timepicker/

Utilizzo
--------

Estendere AdminModelForm, e ridefinire i fields su cui si vuole applicare il widget forms.py::
	
	#mostra sia il date che il time picker
	date_begin= forms.DateTimeField(required = False,
		widget=DateTimePicker(attrs={'class': 'hasDateTimePicker',}))
	
	#mostra solo il date picker
	date_end = forms.DateField(required = False,
		widget=DateTimePicker(attrs={'class': 'hasDatePicker',}))
	
	#mostra solo il time picker
	date_end = forms.TimeField(required = False,
		widget=DateTimePicker(attrs={'class': 'hasTimePicker',}))
	

