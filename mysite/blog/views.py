from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.core.paginator import Paginator, EmptyPage,\
                                  PageNotAnInteger

from django.core.mail import send_mail
from django.db.models import Count

from .models import Post,Comment
from .forms import EmailPostForm, CommentForm
from taggit.models import Tag


def post_list(request, tag_slug=None):
    data = Post.published.all()
    tag = None
    
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        data = data.filter(tags__in=[tag])
    paginator = Paginator(data, 3) # 3 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        #if page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deleiver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/list.html',
                  {'posts': posts,
                   'page': page,
                   'tag': tag})



# class PostListView(ListView):
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                                   status='published',
                                   publish__year=year,
                                   publish__month=month,
                                   publish__day=day)
    
    comments = post.comments.filter(active=True)

    new_comment = None
    
    if request.method == "POST":
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid:
            #Create a comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            #Assign the current post to the comment
            new_comment.post = post
            #now save the comment
            new_comment.save()
    else:
        comment_form = CommentForm()  
    #list of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    print("*"*450)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    print("_" * 450)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
                                 .order_by('-same_tags', '-publish')[:4]
    return render(request, 
                  'blog/post/detail.html',
                  {'post': post,
                   'comments':comments,
                   'new_comment': new_comment,
                   'comment_form': comment_form,
                   'similar_posts': similar_posts})




def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = f"{cd['name']} recommends you read "\
                      f"{post.title}"
            message = f'Read {post.title} at {post_url}\n\n'\
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
        else:
            raise form.ValidatedError
    
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html',
                            {'post': post,
                             'form': form,
                             'sent': sent})

