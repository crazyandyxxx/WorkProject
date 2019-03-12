import json
import sys
import time
from flask import render_template
from rq import get_current_job
from app import create_app, db
from app.models import User, Post, Task
from app.email import send_email

app = create_app()
app.app_context().push()


def _set_task_progress(progress, task_id, user):
    # job = get_current_job()
    # if job:
    if True:
        # job.meta['progress'] = progress
        # job.save_meta()
        task = Task.query.get(task_id)
        user.add_notification('task_progress', {'task_id': task_id,
                                                     'progress': progress})
        if progress >= 100:
            task.complete = True
        db.session.commit()


def export_posts(user_id, task_id):
    try:
        user = User.query.get(user_id)
        _set_task_progress(0, task_id, user)
        data = []
        i = 0
        total_posts = user.posts.count()
        for post in user.posts.order_by(Post.timestamp.asc()):
            data.append({'body': post.body,
                         'timestamp': post.timestamp.isoformat() + 'Z'})
            time.sleep(5)
            i += 1
            _set_task_progress(100 * i // total_posts, task_id, user)

        # send_email('[Microblog] Your blog posts',
        #         sender=app.config['ADMINS'][0], recipients=[user.email],
        #         text_body=render_template('email/export_posts.txt', user=user),
        #         html_body=render_template('email/export_posts.html',
        #                                   user=user),
        #         attachments=[('posts.json', 'application/json',
        #                       json.dumps({'posts': data}, indent=4))],
        #         sync=True)
    except:
        _set_task_progress(100, task_id, user)
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
