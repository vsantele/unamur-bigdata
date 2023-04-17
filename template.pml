physical schemas { 
	
	document schema mymongo {
		collection actorCollection {
			fields {
				id,
				fullname,
				birthyear,
				deathyear,
				movies[0-N]{
					id,
					title,
					rating[1]{
						rate,
						numberofvotes
					}
				}
			}
		}
	}
	
	key value schema myredis {
		kvpairs movieKV {
			key : "movie:"[id],
			value : hash{
				title,
				originalTitle,
				isAdult,
				startYear,
				runtimeMinutes
			}
		}
	}
	
	relational schema myrel {
		table directorTable{
			columns{
				id,
				fullname,
				birth,
				death
			}
		}
		
		
		table directed {
			columns{
				director_id,
				movie_id
			}
			references {
				director_id -> myrel.directorTable.id
				movie_id -> myredis.movieKV.id
				movie_id -> mymono.actorCollection.movies.id
			}
		}
	}
}