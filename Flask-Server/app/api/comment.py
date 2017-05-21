# *-* coding: utf-8 *-*
from flask import request
from app.utils import UUID
from flask_login import current_user
from app.models import Comment, Movie, db
from flask_restplus import Namespace, Resource

api = Namespace('comment', description='评论模块')

@api.route('/')
class CommentsResource(Resource):
    @api.doc(parser=api.parser().add_argument('movieId', type=str, required=True, help='电影id', location='args'))
    def get(self):
        """获取评论列表"""
        movieId = request.args.get('movieId', '')
        movie = Movie.query.get(movieId)
        if movie is None:
            return {'message': '电影不存在'}, 233

        return [c.__json__() for c in movie.comments], 200


    @api.doc(parser=api.parser()
                    .add_argument('movieId', type=str, required=True, help='电影id', location='form')
                    .add_argument('rating', type=int, required=True, help='评分(1-5)', location='form')
                    .add_argument('content', type=str, required=True, help='评论内容', location='form'))
    def post(self):
        form = request.form
        movieId = form.get('movieId', '')
        movie = Movie.query.get(movieId)
        if movie is None:
            return {'message': '电影不存在'}, 233

        try:
            rating = form.get('rating', '')
            rating = int(rating)
            if rating < 0 or rating > 5:
                return {'message': '评分非法'}, 233
        except Exception:
            return {'message': '评分非法'}, 233

        content = form.get('content', '')
        if len(content.strip()) == 0:
            return {'message': '评论内容不能为空'}, 233

        comment = Comment()
        comment.id = UUID()
        comment.rating = rating
        comment.content = content
        comment.movieId = movieId
        comment.username = current_user.id
        db.session.add(comment)

        total = movie.ratingNum * movie.rating
        movie.ratingNum += 1
        movie.rating = (total + rating) / movie.ratingNum
        db.session.commit()

        return {'message':'评论成功'}, 200


@api.route('/<id>')
@api.doc(params={'id': '评论id'})
class CommentResource(Resource):
    def get(self, id):
        """获取评论详情"""
        comment = Comment.query.get(id)
        if comment is None:
            return {'message': '评论不存在'}, 233
        return comment.__json__(), 200