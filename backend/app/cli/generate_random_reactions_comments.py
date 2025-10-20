import random
from backend.app.db.session import SessionLocal
from backend.app.db.models import Woulate, Reaction, Comment, ReactionType, User

# Arabic reactions and comments
REACTIONS = [ReactionType.LIKE, ReactionType.LOVE, ReactionType.DISLIKE,
             ReactionType.ANGRY,ReactionType.CRY]

COMMENTS = [
    "تعيين ممتاز!",
    "نتمنى له التوفيق في مهامه الجديدة",
    "اختيار غير مناسب لهذه المسؤولية",
    "لديه خبرة كافية لهذا المنصب",
    "نأمل أن يخدم مصالح المواطنين",
    "هذا التعيين لا يلبي تطلعات الساكنة",
    "شخص كفء وذو خبرة إدارية",
    "نطالب بمزيد من الشفافية في التعيينات",
    "نتمنى أن يحسن التدبير الإداري",
    " تعيين جيد يستحق الترحيب",
    "تعيين جيد يستحق الترحيب",
    "لماذا تم اختياره دون غيره؟",
    "نأمل أن يكون عند حسن الظن",
    "شخصية معروفة بنزاهتها",
    "خير اختيار لهذا المنصب",
    "ننتظر نتائج عمله بفارغ الصبر",
    "يجب أن يكون أكثر قربا من المواطنين",
    "نأمل أن يحقق تغييرات إيجابية",
    "هذا التعيين يثير الكثير من التساؤلات",
    "هذا الشخص لديه سجل حافل بالنجاحات",
    "هذا التعيين يبعث على الأمل",
    "نأمل أن يكون عند مستوى التحديات",
    "يجب أن يكون أكثر شفافية في عمله",
    "هذا التعيين مفاجئ وغير متوقع",
    "نتمنى له النجاح في مهامه الصعبة"
]

def generate_reactions_and_comments():
    db = SessionLocal()
    try:
        # Get all users
        users = db.query(User).all()
        if not users:
            print("No users found!")
            return
        
        # Get all woulate for jiha_id = 6 (جهة الدار البيضاء سطات)
        woulate_list = db.query(Woulate).filter(Woulate.jiha_id == 6).all()
        if not woulate_list:
            print("❌ No woulate found for jiha_id = 6!")
            return
        
        print(f"Found {len(woulate_list)} woulate and {len(users)} users")
        
        reactions_count = 0
        comments_count = 0
        
        for woulate in woulate_list:
            # Each woulate gets 1-3 random reactions from random users
            num_reactions = random.randint(1, min(3, len(users)))
            selected_users_for_reactions = random.sample(users, num_reactions)
            
            for user in selected_users_for_reactions:
                # Check if reaction already exists
                existing_reaction = db.query(Reaction).filter(
                    Reaction.woulate_id == woulate.id,
                    Reaction.user_id == user.id
                ).first()
                
                if not existing_reaction:
                    reaction = Reaction(
                        woulate_id=woulate.id,
                        user_id=user.id,
                        reaction_type=random.choice(REACTIONS)
                    )
                    db.add(reaction)
                    reactions_count += 1
            
            # Each woulate gets 0-2 random comments from random users
            num_comments = random.randint(0, min(2, len(users)))
            if num_comments > 0:
                selected_users_for_comments = random.sample(users, num_comments)
                for user in selected_users_for_comments:
                    comment = Comment(
                        woulate_id=woulate.id,
                        user_id=user.id,
                        content=random.choice(COMMENTS)
                    )
                    db.add(comment)
                    comments_count += 1
        
        db.commit()
        print(f"Successfully generated {reactions_count} reactions and {comments_count} comments!")
        
        # Show sample data
        sample_reactions = db.query(Reaction).limit(3).all()
        sample_comments = db.query(Comment).limit(3).all()
        
        print("\n📊 Sample Reactions:")
        for r in sample_reactions:
            woulate = db.query(Woulate).filter(Woulate.id == r.woulate_id).first()
            user = db.query(User).filter(User.id == r.user_id).first()
            print(f"{user.username} reacted with {r.reaction_type.value} to {woulate.full_name}")
        
        print("\n💬 Sample Comments:")
        for c in sample_comments:
            woulate = db.query(Woulate).filter(Woulate.id == c.woulate_id).first()
            user = db.query(User).filter(User.id == c.user_id).first()
            print(f"{user.username}: \"{c.content}\" on {woulate.full_name}")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_reactions_and_comments()