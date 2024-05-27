from django.urls import path
from . views import *
from .encrypt_url import urlEncryption, urlEncoding

urlpatterns = [
    path(f"{urlEncryption('main')}{urlEncoding('main')}/", main, name='main'),
    path(f"{urlEncryption('new_post')}{urlEncoding('new_post')}/", newPost, name='new_post'),
    path(f"{urlEncryption('refresh')}{urlEncoding('refresh')}/<str:user_provided_id>/", refresh, name='refresh'),
    path(f"{urlEncryption('add_post')}{urlEncoding('add_post')}/<str:post_id>/", addPost, name='add_post'),
    path(f"{urlEncryption('new_post_manually')}{urlEncoding('new_post_manually')}", new_post_manually, name='new_post_manually'),
    path(f"{urlEncryption('edit_post')}{urlEncoding('edit_post')}/<str:post_id>/", editPost, name='edit_post'),
    path(f"{urlEncryption('delete_post')}{urlEncoding('delete_post')}/<str:post_id>/", deletePost, name='delete_post'),
    path(f"{urlEncryption('save_post')}{urlEncoding('save_post')}/<str:post_id>/", savePost, name='save_post'),
    path(f"{urlEncryption('post_details')}{urlEncoding('post_details')}/<str:post_id>/", postDetail, name='post_detail'),
    path(f"{urlEncryption('search')}{urlEncoding('search')}/", search_results, name='search_results'),
    path(f"{urlEncryption('graph_anaylsis')}{urlEncoding('graph_anaylsis')}/<str:post_id>/", graphAnaylsis, name='graph_anaylsis'),
    path(f"{urlEncryption('help')}{urlEncoding('help')}/", help, name='help'),
    path(f"{urlEncryption('comparison')}{urlEncoding('comparison')}/", usersComparison, name='comparison'),
    # path(f"{urlEncryption('export_data')}{urlEncoding('export_data')}/", export_data, name='export_data'),
    path(f"{urlEncryption('export_data')}{urlEncoding('export_data')}/", export_data_json, name='export_data_json'),
    path(f"{urlEncryption('compare_users')}{urlEncoding('compare_users')}/", compare_users, name='compare_users'),
    path(f"{urlEncryption('kill_switch')}{urlEncoding('kill_switch')}/<str:post_id>/", kill_switch, name='kill_switch'),
]