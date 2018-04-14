import numpy as np

class Controller():
    ATTACK_ENERGY = 25
    CONVERT_ENERGY = 75
    CONSTRUCT_ENERGY = 75
    DECONSTRUCT_ENERGY = 75
    PICKUP_ENERGY = 1

    FRESH_HUMAN_TITLE = 'fresh human'
    CAT_OVERLORD_TITLE = 'cat overlord'
    SOLDIER_TITLE = 'soldier'
    GATHERER_TITLE = 'gatherer'
    BUILDER_TITLE = 'builder'
    MISSIONARY_TITLE = 'missionary'

    MISSIONARY_NUMBER_OF_MOVES = 4

    SHELTER_TITLE = 'shelter'

    MATERIALS_FOR_SHELTER = 50

    UNITS_TO_START_WITH = [MISSIONARY_TITLE, SOLDIER_TITLE, GATHERER_TITLE] 

    def __init__(self, ai, player):
        self.ai = ai
        self.game = ai.game
        self.units = player.units
        self.king = player.cat
        self.enemy_structures = player.opponent.structures
        self.enemy_king = player.opponent.cat
        self.enemy_units = player.opponent.units
        self.structures = player.structures
        self.initialized = False
        self.player = player
        self.road = [road for road in self.game.structures if road.type == 'road']
        self.resting = {}

    @property
    def ai(self):
        return self._ai

    @ai.setter
    def ai(self, value):
        self._ai = value

    @property
    def road(self):
        return self._road

    @road.setter
    def road(self, value):
        self._road = value

    @property
    def game(self):
        return self._game

    @game.setter
    def game(self, value):
        self._game = value
    
    @property
    def bushes(self):
        return [bush for bush in self.game.tiles if bush.turns_to_harvest == 0 and bush.harvest_rate > 0]

    @property
    def enemy_structures(self):
        return self._enemy_structures
    
    @enemy_structures.setter
    def enemy_structures(self, value):
        self._enemy_structures = value

    @property
    def enemy_king(self):
        return self._enemy_king

    @enemy_king.setter
    def enemy_king(self, value):
        self._enemy_king = value
    
    @property
    def materials(self):
        neutral_structures = [neutral for neutral in self.game.structures if neutral.type == 'neutral']
        enemy_shelters = [shelter for shelter in self.enemy_structures if shelter.type == 'shelter']
        return neutral_structures if neutral_structures else enemy_shelters

    @property
    def king(self):
        return self._king
    
    @king.setter
    def king(self, value):
        self._king = value

    @property
    def units(self):
        return self._units
    
    @units.setter
    def units(self, value):
        self._units = value

    @property
    def structures(self):
        return self._structures

    @structures.setter
    def structures(self, value):
        self._structures = value
    
    @property
    def initialized(self):
        value = self._initialized
        self.initialized = True
        return value

    @initialized.setter
    def initialized(self, value):
        self._initialized = value

    @property
    def convertible_units(self):
        return [unit for unit in self.game.units if unit.owner is None]
    
    @property
    def fresh_humans(self):
        return [unit for unit in self.units if unit.job.title == self.FRESH_HUMAN_TITLE]
    
    @property
    def missionaries(self):
        return [unit for unit in self.units if unit.job.title == self.MISSIONARY_TITLE]

    @property
    def gatherers(self):
        return [unit for unit in self.units if unit.job.title == self.GATHERER_TITLE]
    
    @property
    def builders(self):
        return [unit for unit in self.units if unit.job.title == self.BUILDER_TITLE]

    @property
    def soldiers(self):
        return [unit for unit in self.units if unit.job.title == self.SOLDIER_TITLE]
    
    @property
    def shelters(self):
        return [structure for structure in self.structures if structure.type == self.SHELTER_TITLE]

    def get_tile_around_cat_overlord(self):
        king_x, king_y = (self.king.tile.x, self.king.tile.y)
        goal = self.king.tile

        for x in (king_x-1, king_x, king_x+1):
            for y in (king_y-1, king_y, king_y+1):
                if x != king_x or y != king_y:
                    tile = self.game.get_tile_at(x, y)
                    if tile and tile.is_pathable():
                        goal = tile
                        break
        
        return goal
    
    def get_shelter_positions(self):
        return [np.array([shelter.tile.x, shelter.tile.y]) for shelter in self.shelters]

    def get_road_positions(self):
        return [np.array([road.tile.x, road.tile.y]) for road in self.road]

    def get_materials_positions(self):
        return [np.array([materials.tile.x, materials.tile.y]) for materials in self.materials]

    def get_bush_positions(self):
        return [np.array([bush.x, bush.y]) for bush in self.bushes]
    
    def get_unit_position(self, unit):
        return np.array([unit.tile.x, unit.tile.y])
    
    def get_unit_positions(self, units):
        return [self.get_unit_position(unit) for unit in units]

    def get_enemey_unit_positions(self):
        return [np.array([unit.tile.x, unit.tile.y]) for unit in self.enemy_units]
    
    def get_target(self, a, b):
        distances = np.sum((b-a[None, :])**2, axis=1)
        return np.argmin(distances)

    def get_distance_to(self, tile_a, tile_b):
        return np.sqrt(np.sum((np.array([tile_a.x, tile_a.y])-np.array([tile_b.x, tile_b.y]))**2))

    def return_to_base(self, units, energy_threshold, change_job=None):
        for unit in units:           
            if unit.energy < energy_threshold:
                if change_job is None:
                    shelters = self.shelters
                    goal = shelters[self.get_target(self.get_unit_position(unit), self.get_shelter_positions())]
                else:
                    goal = self.get_tile_around_cat_overlord()
                
                path = self.ai.find_path(unit.tile, goal.tile if not isinstance(goal, type(unit.tile)) else goal)

                if change_job is None:
                    if self.get_distance_to(unit.tile, goal.tile) <= 1 and unit.energy < 100:
                        unit.rest()

                for tile in path:
                    threshold = 1 if change_job is None else np.sqrt(2)+.1
                    if self.get_distance_to(unit.tile, goal.tile if change_job is None else self.king.tile) <= threshold:
                        if change_job is None and unit.energy < 100:
                            unit.rest()
                            if unit.food > 0 and hasattr(goal, 'tile') and goal.tile.structure and goal.tile.structure.type == 'shelter':
                                unit.drop(goal.tile, 'food', -1)
                        elif change_job is not None:
                            unit.change_job(change_job)
                        
                        break
                    if unit.moves > 0:
                        unit.move(tile)
                    else:
                        break
                        
    def run_missionary_controller(self):
        missionaries = self.missionaries
        fresh_humans = self.convertible_units
        if missionaries:
            if fresh_humans:
                fresh_human_positions = self.get_unit_positions(fresh_humans)
                for missionary in missionaries:
                    if missionary.energy >= self.CONVERT_ENERGY:
                        goal = fresh_humans[self.get_target(self.get_unit_position(missionary), fresh_human_positions)]
                        path = self.ai.find_path(missionary.tile, goal.tile)
                        for tile in path:
                            if self.get_distance_to(missionary.tile, goal.tile) == 1:
                                missionary.convert(goal.tile)
                                break
                            if missionary.moves > 0:
                                missionary.move(tile)
                            else:
                                break
            
            self.return_to_base(missionaries, self.CONVERT_ENERGY)

    def run_fresh_human_controller(self):
        fresh_humans = self.fresh_humans
        if fresh_humans:
            job_title = self.SOLDIER_TITLE
            if not len(self.missionaries):
                job_title = self.MISSIONARY_TITLE
            elif not len(self.builders):
                job_title = self.BUILDER_TITLE
            elif len(self.gatherers) < 2:
                job_title = self.GATHERER_TITLE
            
            self.return_to_base(fresh_humans, np.inf, change_job=job_title)

    def run_gatherer_controller(self):
        gatherers = self.gatherers
        bushes = self.bushes

        if gatherers:
            if bushes:
                bush_positions = self.get_bush_positions()
                for gatherer in gatherers:
                    if not gatherer.food and gatherer.energy >= 75: 
                        goal = bushes[self.get_target(self.get_unit_position(gatherer), bush_positions)]
                        path = self.ai.find_path(gatherer.tile, goal)
                        for tile in path:
                            if self.get_distance_to(gatherer.tile, goal) == 1:
                                gatherer.harvest(goal)
                                break
                            if gatherer.moves > 0:
                                gatherer.move(tile)
                            else:
                                break
                
                self.return_to_base([gatherer for gatherer in self.gatherers if gatherer.food > 0 or gatherer.energy < 75], np.inf)

    def run_builder_controller(self):
        builders = self.builders
        materials = self.materials

        if builders:
            if materials:
                materials_positions = self.get_materials_positions()
                for builder in builders:
                    if builder.energy >= self.CONSTRUCT_ENERGY:
                        if builder.materials < self.MATERIALS_FOR_SHELTER:
                            goal = materials[self.get_target(self.get_unit_position(builder), materials_positions)]
                            path = self.ai.find_path(builder.tile, goal.tile)
                            for tile in path:
                                if self.get_distance_to(builder.tile, goal.tile) == 1:
                                    builder.deconstruct(goal.tile)
                                    break
                                if builder.moves > 0:
                                    builder.move(tile)
                                else:
                                    break
                        else:
                            road_positions = self.get_road_positions()
                            goal = self.road[self.get_target(self.get_unit_position(builder), road_positions)]
                            target_y = goal.tile.y-1 if builder.tile.y < goal.tile.y else goal.tile.y+1
                            distance = np.inf
                            for x in range(0, self.game.map_width):
                                tile = self.game.get_tile_at(x, target_y)
                                distance_to_goal = self.get_distance_to(builder.tile, tile)
                                if tile.is_pathable() and tile.structure is None and distance_to_goal < distance:
                                    distance = distance_to_goal
                                    goal = tile
                            
                            path = self.ai.find_path(builder.tile, goal)

                            for tile in path:
                                if self.get_distance_to(builder.tile, goal) == 1:
                                    builder.drop(goal, 'material', self.MATERIALS_FOR_SHELTER)
                                    builder.construct(goal, 'shelter')
                                    break
                                if builder.moves > 0:
                                    builder.move(tile)
                                else:
                                    break

                self.return_to_base(builders, self.CONSTRUCT_ENERGY)

    def get_enemy_tile_by_soldier(self, soldier):
        enemy_tile = None
        enemy_energy = np.inf

        for neighbor in soldier.tile.get_neighbors():
            if neighbor.unit and neighbor.unit.job.title != self.FRESH_HUMAN_TITLE and neighbor.unit.owner is not self.player and neighbor.unit.energy < enemy_energy:
                enemy_energy = neighbor.unit.energy
                enemy_tile = neighbor

        return enemy_tile

    def run_soldier_controller(self):
        soldiers = self.soldiers
        enemy_units = self.enemy_units

        for soldier in soldiers:
            nearby_enemy = self.get_enemy_tile_by_soldier(soldier)
            if soldier.energy == 100:
                self.resting[soldier] = False
            if soldier.energy > self.ATTACK_ENERGY and nearby_enemy:
                soldier.attack(nearby_enemy)
            if not self.resting.get(soldier) and len(soldiers) >= 3:
                goal = enemy_units[self.get_target(self.get_unit_position(soldier), self.get_enemey_unit_positions())]
                path = self.ai.find_path(soldier.tile, goal.tile)

                for tile in path:
                    if soldier.energy <= self.ATTACK_ENERGY:
                        self.resting[soldier] = True
                        break
                    if soldier.energy > self.ATTACK_ENERGY and nearby_enemy:
                        soldier.attack(nearby_enemy)
                    if soldier.moves > 0:
                        soldier.move(tile)
                        nearby_enemy = self.get_enemy_tile_by_soldier(soldier)
                    else:
                        break
        
        self.return_to_base([soldier for soldier, value in self.resting.items() if value], 100)

    def run_turn(self):
        if not self.initialized:
            for title, unit in zip(self.UNITS_TO_START_WITH, self.fresh_humans):
                unit.change_job(title)
        self.run_missionary_controller()
        self.run_fresh_human_controller()
        self.run_gatherer_controller()
        self.run_builder_controller()
        self.run_soldier_controller()