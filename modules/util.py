def normalizeUsers( p ):

    db = p.db

    authUsers = db( db.auth_user.id > 0 ).select( orderby = db.auth_user.last_name )

    for user in authUsers:

        if( db( db.unique_user.last_name == user.last_name ).count() == 0 ):

            uniqueUserId = db.unique_user.insert( first_name = user.first_name, last_name = user.last_name )

            db.user_map.insert( auth_user_id = user.id, unique_user_id = uniqueUserId )

        elif( db( ( db.unique_user.last_name == user.last_name ) &
                  ( db.unique_user.first_name == user.first_name) ).count() == 1 ):

            uniqueUserId = db( ( db.unique_user.last_name == user.last_name ) &
                               ( db.unique_user.first_name == user.first_name) ).select()[0].id

            if( db( ( db.user_map.unique_user_id == uniqueUserId ) &
                    ( db.user_map.auth_user_id == user.id ) ).count() == 0 ):

                    db.user_map.insert( auth_user_id = user.id, unique_user_id = uniqueUserId )

        else:

            sameLastNames = db( db.unique_user.last_name == user.last_name ).select()

            found = False

            for person in sameLastNames:

                if( ( person.first_name in user.first_name ) or
                    ( user.first_name in person.first_name ) ):

                    found = True

                    if( db( ( db.user_map.unique_user_id == person.id ) &
                            ( db.user_map.auth_user_id == user.id ) ).count() == 0 ):

                            db.user_map.insert( auth_user_id = user.id, unique_user_id = person.id )

                    break

            if( found == False ):

                uniqueUserId = db.unique_user.insert( first_name = user.first_name, last_name = user.last_name )

                db.user_map.insert( auth_user_id = user.id, unique_user_id = uniqueUserId )
