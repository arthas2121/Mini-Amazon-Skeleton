from flask import current_app as app, flash
from datetime import datetime

from sqlalchemy import false

class productReview:
    def __init__(self, uid, pid, rating, description, review_time):
        self.uid = uid
        self.pid = pid
        self.rating = rating
        self.description = description
        self.review_time = review_time

    def get_product_review_from_high(pid):
        rows = app.db.execute(
        """ SELECT uid, rating, description, review_time, like_num, filename FROM ProductReview
            WHERE pid =:pid
            ORDER BY rating DESC
        """, pid = pid
        )
        return rows;

    def get_product_review_from_low(pid):
        rows = app.db.execute(
        """ SELECT uid, rating, description, review_time, like_num, filename FROM ProductReview
            WHERE pid =:pid
            ORDER BY rating ASC
        """, pid = pid
        )
        return rows;

    def get_product_review_new_date(pid):
        rows = app.db.execute(
        """ SELECT uid, rating, description, review_time, like_num, filename FROM ProductReview
            WHERE pid =:pid
            ORDER BY review_time DESC
        """, pid = pid
        )
        return rows;

    def add_product_review(uid, pid, rating, description):
        purchase = app.db.execute(
            """ SELECT pid FROM Orders
            WHERE buyer_uid =:uid AND pid =:pid 
            """, uid = uid, pid = pid
        )
        if purchase == []:
            flash("You can only review if you have purchased the item!")
            return 0

        reviews = app.db.execute(
            """ SELECT pid FROM ProductReview 
            WHERE uid =:uid AND pid =:pid 
            """, uid = uid, pid = pid
        )
        if reviews != []:
            flash("You have already made a review for this item!")
            return 1
        
        review_time = datetime.now()
        app.db.execute(
            """ INSERT INTO ProductReview(uid, pid, rating, description, review_time, like_num)
            VALUES(:uid, :pid, :rating, :description, :review_time, 0)
            RETURNING uid
            """, uid = uid, pid = pid, rating = rating, description = description, review_time = review_time
        )
        flash("Review added successfully!")
        return True

    def update_product_review(uid, pid, rating, description):
        review_time = datetime.now()
        app.db.execute(
            """ UPDATE ProductReview
            SET rating =:rating, description =:description, review_time =:review_time
            WHERE pid =:pid and uid=:uid
            RETURNING *
            """, rating = rating, description = description, review_time = review_time, uid=uid, pid = pid
        )
        return 0

    def get_user_product_review(uid, pid):
        reviews = app.db.execute(
            """SELECT * FROM ProductReview 
            WHERE uid=:uid and pid =:pid
            """, uid = uid, pid = pid
        )
        return reviews
    
    def get_user_all_product_reviews(uid):
        reviews = app.db.execute(
            """ SELECT * FROM ProductReview
            WHERE uid=:uid
            ORDER BY review_time DESC
            """, uid=uid
        )
        return reviews

    def get_product_avg_review(pid):
        rows = app.db.execute(
            """ SELECT AVG(rating)::numeric(10,1) as avg
            FROM ProductReview
            WHERE pid=:pid
            GROUP BY pid
            """, pid = pid
        )

        if rows == []:
            return 0.0

        return rows[0][0]
    
    def get_num_product_review(pid):
        rows = app.db.execute(
            """ SELECT COUNT(rating) as cnt
            FROM ProductReview
            WHERE pid=:pid
            GROUP BY pid
            """, pid=pid
        )

        if rows == [] or 0:
            return 0
        return rows[0][0]

    def remove_product_review(uid, pid):
        app.db.execute(
            """ DELETE FROM ProductReview
            WHERE uid=:uid AND pid=:pid
            RETURNING uid
            """, uid=uid, pid=pid
        )
        flash("Review Removed!")
        return uid

    def like_product_review(uid, pid):
        rows = app.db.execute(
            """ UPDATE ProductReview
            SET like_num = like_num + 1
            WHERE uid =:uid AND pid =:pid
            """, uid=uid, pid=pid
        )

        return rows
    
    def dislike_product_review(uid, pid):
        rows = app.db.execute(
            """ UPDATE ProductReview
            SET like_num = like_num - 1
            WHERE uid =:uid AND pid =:pid
            """, uid=uid, pid=pid
        )

        return rows

    def get_top_3_reviews(pid):
        rows = app.db.execute(
            """ SELECT uid, rating, description, review_time, like_num
            FROM ProductReview WHERE pid=:pid
            ORDER BY like_num DESC
            LIMIT 3
            """, pid=pid
        )
        return rows

    def update_image_path(pid, uid, filename):
        app.db.execute(
            """ UPDATE ProductReview
            SET filename=:filename
            WHERE pid=:pid and uid=:uid
            """, filename=filename, uid=uid, pid=pid
        )
        return 0
    
    def get_user_product_image_path(pid, uid):
        rows = app.db.execute(
            """ SELECT filename
            FROM ProductReview
            WHERE pid=:pid and uid=:uid
            """, pid=pid, uid=uid
        )
        return rows[0][0]

    def get_product_image_path(pid):
        reviews = app.db.execute(
            """ SELECT uid, rating, description, review_time, like_num, filename
            FROM ProductReview
            WHERE pid=:pid and filename is not NULL
            ORDER BY like_num DESC
            """, pid=pid
        )
        return reviews