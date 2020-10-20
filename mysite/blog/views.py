from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage,\
                                  PageNotAnInteger

from django.core.mail import send_mail

# def post_list(request):
#     data = Post.published.all()
#     paginator = Paginator(data, 3) # 3 posts in each page
#     page = request.GET.get('page')
#     try:
#         posts = paginator.page(page)
#     except PageNotAnInteger:
#         #if page is not an integer deliver the first page
#         posts = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range deleiver last page of results
#         posts = paginator.page(paginator.num_pages)
#     return render(request,
#                   'blog/post/list.html',
#                   {'posts': posts,
#                    'page': page})

from django.views.generic import ListView

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                                   status='published',
                                   publish__year=year,
                                   publish__month=month,
                                   publish__day=day)
    return render(request, 
                  'blog/post/detail.html',
                  {'post': post})


from .forms import EmailPostForm

def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method = "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_url(
                post.get_absolute_url()
            )
            subject = f"{cd['name']} recommends you read "\
                      f"{post.title}"
            message = f'Read {post.title} at {post_url}\n\n"\
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_name(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
        else:
            raise form.ValidatedError
    
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html',
                            {'post': post,
                             'form': form,
                             'sent': sent})
