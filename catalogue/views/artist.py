from django.shortcuts import redirect, render, get_object_or_404
from django.http import Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from catalogue.utils import admin_check
from django.conf import settings
from catalogue.models import Artist
from catalogue.forms import ArtistForm

#...

def group_required(group_name):
    def decorator(view_func):
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.groups.filter(name=group_name).exists():
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

@user_passes_test(admin_check)
def create(request):
    if not request.user.is_authenticated or not request.user.has_perm('add_artist'):
        return redirect(f"{settings.LOGIN_URL}?next={request.path}")

    form = ArtistForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Nouvel artiste créé avec succès.")

            return redirect('catalogue:artist-index')
        else:
            messages.add_message(request, messages.ERROR, "Échec de l'ajout d'un nouvel artiste !")

    return render(request, 'artist/create.html', {
        'form' : form,
    })

def admin_check(user):
    return user.is_staff  # V

@login_required
def edit(request, artist_id): 
    # fetch the object related to passed id
    artist = Artist.objects.get(id=artist_id)

    # pass the object as instance in form
    form = ArtistForm(request.POST or None, instance = artist)
    
    if request.method == 'POST':    #TODO http_override doesn't work
        # save the data from the form and
        # redirect to detail_view
        if form.is_valid():
            form.save()
            messages.success(request, "Artiste modifié avec succès.")

            return render(request, "artist/show.html", {
                'artist' : artist,
            })
        else:
            messages.error(request, "Échec de la modification de l'artiste !")

    return render(request, 'artist/edit.html', {
        'form' : form,
        'artist' : artist,
    })

@login_required
@permission_required('catalog.can_delete', raise_exception=True)
def delete(request, artist_id): 
    artist = get_object_or_404(Artist, id = artist_id)

    if request.method =="POST":
        artist.delete()
        messages.success(request, "Artiste supprimé avec succès.")

        return redirect('catalogue:artist-index')
    else:
        messages.error(request, "Échec de la suppression de l'artiste !")

    return render(request, 'artist/show.html', {
        'artist' : artist,
    })


# Create your views here.
def index(request):
	artists = Artist.objects.all()
	
	return render(request, 'artist/index.html', {
		'artists' : artists,
	})


def show(request, artist_id):
	try:
		artist = Artist.objects.get(id=artist_id)
	except Artist.DoesNotExist:
		raise Http404('Artist inexistant')
		
	return render(request, 'artist/show.html', {
		'artist' : artist,
	})


