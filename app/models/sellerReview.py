from flask import current_app as app, flash
from datetime import datetime

class sellerReview:
    def __init__(self, uid, sid, rating, description, review_time):
        self.uid = uid
        self.sid = sid
        self.rating = rating
        self.description = description
        self.review_time = review_time

    def get_seller_review_from_high(sid):
        rows = app.db.execute(
        """ SELECT uid, rating, description, review_time FROM SellerReview
            WHERE sid =:sid
            ORDER BY rating DESC
        """, sid = sid
        )
        return rows;

    def get_seller_review_from_low(sid):
        rows = app.db.execute(
        """ SELECT uid, rating, description, review_time FROM SellerReview
            WHERE sid =:sid
            ORDER BY rating ASC
        """, sid = sid
        )
        return rows;

    def get_seller_review_new_date(sid):
        rows = app.db.execute(
        """ SELECT uid, rating, description, review_time FROM SellerReview
            WHERE sid =:sid
            ORDER BY review_time DESC
        """, sid = sid
        )
        return rows;

    def add_seller_review(uid, sid, rating, description):
        purchase = app.db.execute(
            """ SELECT pid FROM Orders 
            WHERE buyer_uid =:uid AND seller_uid =:sid 
            """, uid = uid, sid = sid
        )
        if purchase == []:
            flash("You can only review a seller after you make a purchase from them!")
            return 0

        reviews = app.db.execute(
            """ SELECT sid FROM SellerReview 
            WHERE uid =:uid AND sid =:sid 
            """, uid = uid, sid = sid
        )
        if reviews != []:
            flash("You have already made a review for this seller!")
            return 1
        
        review_time = datetime.now()
        app.db.execute(
            """ INSERT INTO SellerReview(uid, sid, rating, description, review_time, like_num)
            VALUES(:uid, :sid, :rating, :description, :review_time, 0)
            RETURNING uid
            """, uid = uid, sid = sid, rating = rating, description = description, review_time = review_time
        )
        flash("Review added successfully!")
        return True

    def update_seller_review(uid, sid, rating, description):
        review_time = datetime.now()
        app.db.execute(
            """ UPDATE SellerReview
            SET rating =:rating, description =:description, review_time =:review_time
            WHERE uid=:uid and sid=:sid
            RETURNING *
            """, rating = rating, description = description, review_time = review_time, uid=uid, sid=sid
        )
        return 0

    def get_user_seller_review(uid, sid):
        reviews = app.db.execute(
            """ SELECT * FROM SellerReview
            WHERE uid=:uid and sid=:sid
            """, uid=uid, sid=sid
        )
        return reviews

    def get_user_all_seller_reviews(uid):
        reviews = app.db.execute(
            """ SELECT * FROM SellerReview
            WHERE uid =:uid
            ORDER BY review_time DESC
            """, uid = uid
        )
        return reviews
    


    def get_seller_avg_review(sid):
        rows = app.db.execute(
            """ SELECT AVG(rating)::numeric(10,1) as avg
            FROM SellerReview
            WHERE sid=:sid
            GROUP BY sid
            """, sid = sid
        )

        if rows == []:
            return 0.0

        return rows[0][0]
    
    def get_num_seller_review(sid):
        rows = app.db.execute(
            """ SELECT COUNT(rating) as cnt
            FROM SellerReview
            WHERE sid=:sid
            GROUP BY sid
            """, sid=sid
        )

        if rows == [] or 0:
            return 0
        return rows[0][0]

    def remove_seller_review(uid, sid):
        app.db.execute(
            """ DELETE FROM SellerReview
            WHERE uid=:uid AND sid=:sid
            RETURNING uid
            """, uid=uid, sid=sid
        )
        flash("Review Removed!")
        return uid

    def like_seller_review(uid, sid):
        rows = app.db.execute(
            """ UPDATE SellerReview
            SET like_num = like_num + 1
            WHERE uid =:uid AND sid =:sid
            """, uid=uid, sid=sid
        )

        return rows
    
    def dislike_seller_review(uid, sid):
        rows = app.db.execute(
            """ UPDATE SellerReview
            SET like_num = like_num - 1
            WHERE uid =:uid AND sid =:sid
            """, uid=uid, sid=sid
        )

        return rows

    def get_top_3_reviews(sid):
        rows = app.db.execute(
            """ SELECT uid, rating, description, review_time, like_num
            FROM SellerReview WHERE sid=:sid
            ORDER BY like_num DESC
            LIMIT 3
            """, sid=sid
        )
        return rows