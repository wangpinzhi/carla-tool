import carla

class ActorUnit:
    def __init__(self,  name_id:str,
                        actor_id:int,
                        ) -> None:
        self.nameId = name_id
        self.actorId = actor_id

class ActorManager:
    
    def __init__(self, world:carla.World) -> None:
        self.world = world

    def get_actor_by_actorId(self, actorId:int):
        actor = self.world.get_actor(actorId)
        if not actor:
            print(f'Not found actorID:{actorId} actor')
            return
        return actor

    def destroy_all_actors(self):
        pass  
