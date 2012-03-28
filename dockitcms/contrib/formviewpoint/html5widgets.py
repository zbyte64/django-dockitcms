from django.forms.widgets import TextInput

class DateInput(TextInput):
    input_type = 'date'

class DateTimeInput(TextInput):
    input_type = 'datetime'

class EmailInput(TextInput):
    input_type = 'email'

class NumberInput(TextInput):
    input_type = 'number'

class TelephoneInput(TextInput):
    input_type = 'tel'

class URLInput(TextInput):
    input_type = 'url'

