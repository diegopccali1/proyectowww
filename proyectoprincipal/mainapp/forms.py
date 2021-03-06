from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group as Rol
from .models import Profile, Service, Location, Specialty, LocationOnService
from rest_framework import serializers


# Folrmulario para crear y editar un usuario, este formulario se usa para crear un usuario, junto a al formulario de
# perrfil, cuauando se edita solo el perfil solo se habilita uno de los campos de este formulario, el resto se eliminan.
# cuando se edita el usuario completo, se elimina uno de los campos de contraseña y se secambia el tipo de input de pass1
# para que sea visible la nueva clave al escribirla.
class UserForm(UserCreationForm):
    username = forms.CharField(max_length=100, required=True)
    first_name = forms.CharField(max_length=140, required=True)
    last_name = forms.CharField(max_length=140, required=False)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    def __init__(self, *args, **kwargs):
        # Variable que indica que el form se está llamando desde la actualización del perfil
        from_update_profile = kwargs.pop('from_update_profile', False)
        if 'from_update_profile' in kwargs:
            del kwargs['from_update_profile']
        super(UserForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        # Se está actualizando el usuario, por lo tanto no es necesario el campo password de confirmación.
        # También se puede cambiar el campo password1 a texto normal, para ver qué pass se va poner
        if instance and instance.pk:
            self.fields['password1'] = forms.CharField(label='Password', required=False)
            del self.fields['password2']
            self.fields['username'].widget.attrs['readonly'] = True
        # si el formulario se invoca desde la edición de perfil, solo se va a actualizar el pass1, por lo tanto
        # se eliminan todos los otros campos del formulario usuario.
        if from_update_profile:
            del self.fields['username']
            #del self.fields['email']
            del self.fields['first_name']
            del self.fields['last_name']
            del self.fields['is_active']
            del self.fields['is_superuser']

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2',
            'is_active',
            'is_superuser',
            'groups'
        )


# Se usa el mismo formulario para crear y editar uun perfil, además se agrega el formulario de usuario
# para dar la opción de editar la contraseña. Si hay una instancia,
# quiere decir que se va a editar el perfil, por lo tanto, se debe desabilitar los campos no editables
class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if 'request' in kwargs:
            del kwargs['request']
        super(ProfileForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        # if instance and instance.pk:
            # del self.fields['id_card']

    class Meta:
        model = Profile
        fields = ('pic', 'id_card', 'telephone', 'specialty')


class CreateRolForm(forms.ModelForm):
    class Meta:
        model = Rol
        fields = ('id', 'name', 'permissions')



# Se usa el mismo formulario para crear y editar una prioridad
class ServiceForm(forms.ModelForm):
    specialty = forms.ModelChoiceField(Specialty.objects.all())
    class Meta:
        model = Service
        fields = ('id', 'name', 'description', 'status', 'specialty')

# Se usa el mismo formulario para crear y editar una localización
class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ('id', 'name')

class SpecialtyForm(forms.ModelForm):
    class Meta:
        model = Specialty
        fields = ('id', 'name', 'description', 'status')

### Form for channels ###
class ComposeForm(forms.Form):
    message = forms.CharField(
            widget=forms.TextInput(
                attrs={"class": "form-control"}
                )
            )


class LocationOnServiceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LocationOnServiceForm, self).__init__(*args, **kwargs)
        #Ventanillas que están atendiendo, abiertas o pusadas
        open_windows = LocationOnService.objects.exclude(status='4')
        open_windows_ids = []
        for open_window in open_windows:
            open_windows_ids.append(open_window.window_id)
        #Solo se listan ventanillas cerradas
        windows =  Location.objects.exclude(id__in=open_windows_ids)
        self.fields['window'].queryset = windows

    class Meta:
        model = LocationOnService
        fields = ('id', 'status', 'user', 'window')
