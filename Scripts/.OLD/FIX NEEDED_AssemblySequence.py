import rhinoscriptsyntax as rs
import Grasshopper as gh
from Grasshopper.Kernel.Data import GH_Path
import Rhino.Geometry as rg
import networkx as nx
import numpy as np
import itertools
from itertools import combinations

class Trussemble:
    def __init__(self, lines, rigid_points, start_point):
        ## inputs
        self.lines = lines
        self.points, self.connection_tree = self.__get_line_connectivity()
        self.rigid_points = rigid_points
        self.rigid_indices = self.__get_rigid_point_indices()
        self.start_point = start_point
        ## outputs
        self.graph = self.__turn_tree_to_graph(self.connection_tree)
        self.assembly_steps = gh.DataTree[object]()
        self.processed_nodes = []

    def __average_point(self, pt1, pt2, pt3):
        # Calculate the average of the x, y, and z coordinates
        avg_x = (pt1.X + pt2.X + pt3.X) / 3
        avg_y = (pt1.Y + pt2.Y + pt3.Y) / 3
        avg_z = (pt1.Z + pt2.Z + pt3.Z) / 3

        # Return the average point as a Point3d
        average_point = rg.Point3d(avg_x, avg_y, avg_z)
        return average_point

    def __get_rigid_point_indices(self):
        rigid_indices = []
        points_array = np.array([[pt.X, pt.Y, pt.Z] for pt in self.points])

        for rigid_point in self.rigid_points:
            if rigid_point in self.points:
                rigid_indices.append(self.points.index(rigid_point))
            else:
                rigid_point_array = np.array([rigid_point.X, rigid_point.Y, rigid_point.Z])
                distances = np.linalg.norm(points_array - rigid_point_array, axis=1)
                rigid_idx = np.argmin(distances)
                rigid_indices.append(rigid_idx)
        return rigid_indices

    def __get_line_connectivity(self):
        lines = self.lines
        connectivity_tree = gh.DataTree[object]()
        unique_points = {}
        point_index = 0

        for line_index, line in enumerate(lines):
            # Get the start and end points of the line
            start_point = line.From
            end_point = line.To

            # Convert to Point3d objects
            start_point3d = rg.Point3d(start_point.X, start_point.Y, start_point.Z)
            end_point3d = rg.Point3d(end_point.X, end_point.Y, end_point.Z)

            # Add points to the unique points dictionary if they don't already exist
            if start_point3d not in unique_points:
                unique_points[start_point3d] = point_index
                point_index += 1
            if end_point3d not in unique_points:
                unique_points[end_point3d] = point_index
                point_index += 1

            # Get the indices of the start and end points
            start_index = unique_points[start_point3d]
            end_index = unique_points[end_point3d]

            # Append the indices to the connectivity tree
            connectivity_tree.EnsurePath(GH_Path(line_index))  # Create a new branch for the line index
            connectivity_tree.AddRange([start_index, end_index], GH_Path(line_index))

        # Convert unique points to a list of Point3d
        unique_points_list = [None] * len(unique_points)
        for pt, idx in unique_points.items():
            unique_points_list[idx] = pt

        return unique_points_list, connectivity_tree

    def __can_node_be_rigid(self, node):
        graph = self.graph
        neighbours = list(graph.neighbors(node))
        count_existing_neighbours = sum(1 for neighbour in neighbours if neighbour in self.processed_nodes)
        return count_existing_neighbours >= 3

    def __turn_tree_to_graph(self, connections_tree):
        list_of_tuples = []
        for i in range(connections_tree.BranchCount):
            branch = connections_tree.Branch(i)
            if len(branch) == 2:
                list_of_tuples.append(tuple(branch))
        G = nx.Graph()
        G.add_edges_from(list_of_tuples)
        return G

    def __get_first_move(self):
        start_point = self.start_point
        rigid_ids = self.rigid_indices
        points = self.points
        graph = self.graph

        min_avg_distance_to_start = float('inf')
        neighbours_to_connect_to = []
        first_supports = None

        def find_common_neighbour_combinations(graph, rigid_points_indices):
            valid_combinations = []
            common_neighbors = []
            for comb in combinations(rigid_points_indices, 3):
                neighbors_sets = [set(graph.neighbors(node)) for node in comb]
                common_neighbor = set.intersection(*neighbors_sets)
                if common_neighbor:
                    valid_combinations.append(comb)
                    common_neighbors.append(list(common_neighbor)[0])
            return valid_combinations, common_neighbors

        starting_three_candidates, common_neighbours = find_common_neighbour_combinations(graph, rigid_ids)

        for i, starting_three in enumerate(starting_three_candidates):
            p1 = points[starting_three[0]]
            p2 = points[starting_three[1]]
            p3 = points[starting_three[2]]

            centre = self.__average_point(p1, p2, p3)

            avg_distance = (start_point - centre).Length
            if avg_distance < min_avg_distance_to_start:
                min_avg_distance_to_start = avg_distance
                first_supports = starting_three
                neighbours_to_connect_to.append([common_neighbours[i]])

        neighbour_to_connect_to = neighbours_to_connect_to[-1][0]

        self.processed_nodes.extend(first_supports)
        self.processed_nodes.append(neighbour_to_connect_to)
        return list(first_supports), neighbour_to_connect_to

    def __check_missing_edges(self, sub_graph_edges):
        graph = self.graph
        edges_to_add = []

        for node1, node2 in combinations(sub_graph_edges, 2):
            if graph.has_edge(node1, node2):
                edges_to_add.append((node1, node2))

        return edges_to_add

    def __find_unprocessed_neighbors_subgraphs(self):
        graph = self.graph
        processed_nodes = self.processed_nodes
        processed_nodes_set = set(processed_nodes)
        points = self.points

        unprocessed_neighbors = set()
        last_node = processed_nodes[-1]
        neighbors_last_node = set(graph.neighbors(last_node))
        unprocessed_neighbors_last_node = neighbors_last_node - processed_nodes_set

        for node in processed_nodes_set:
            if node == last_node:
                continue
            neighbors = set(graph.neighbors(node))
            unprocessed_neighbors.update(neighbors - processed_nodes_set)

        unprocessed_neighbors.update(unprocessed_neighbors_last_node)

        subgraphs = []
        unprocessed_subgraph = graph.subgraph(unprocessed_neighbors)

        for component in nx.connected_components(unprocessed_subgraph):
            subgraphs.append(list(component))

        subgraphs_sorted = []
        subgraph_last_node = [comp for comp in subgraphs if any(node in unprocessed_neighbors_last_node for node in comp)]
        other_subgraphs = [comp for comp in subgraphs if comp not in subgraph_last_node]

        if subgraph_last_node:
            subgraphs_sorted.extend(subgraph_last_node)
            subgraphs_sorted.extend(other_subgraphs)
            return subgraphs_sorted[0]
        else:
            closest_distance = float('inf')
            first_comp = None
            for comp in subgraphs:
                for node in comp:
                    distance = (points[last_node] - points[node]).Length
                    if distance < closest_distance:
                        first_comp = comp
                        closest_distance = distance
            return first_comp

    def __get_possible_connections(self, node):
        graph = self.graph
        can_connect_to = [neighbour for neighbour in graph.neighbors(node) if neighbour in self.processed_nodes]
        return can_connect_to

    def __sort_rigid_candidates(self, candidates):
        origin = self.processed_nodes[-1]
        points = self.points

        def distance_to_origin(c):
            return (points[origin] - points[c]).Length

        sorted_candidates = sorted(candidates, key=distance_to_origin)
        return sorted_candidates

    def __get_sorted_supports(self, candidate_point, supports):
        support_combinations = list(itertools.combinations(range(len(supports)), 3))
        score_per_combination = {}
        result_supports = []

        def get_combined_distance_to_supports(supports):
            support_coords = np.array([[pt.X, pt.Y, pt.Z] for pt in supports])
            num_supports = len(support_coords)
            diff = support_coords[:, np.newaxis, :] - support_coords[np.newaxis, :, :]
            distances = np.linalg.norm(diff, axis=2)
            # Avoid multiplying by zero by adding small epsilon
            distances += np.eye(num_supports) * 1e-8
            combined_distance = np.prod(distances)
            return combined_distance

        def triangle_area(rs_pointA, rs_pointB, rs_pointC):
            A = np.array([rs_pointA.X, rs_pointA.Y, rs_pointA.Z])
            B = np.array([rs_pointB.X, rs_pointB.Y, rs_pointB.Z])
            C = np.array([rs_pointC.X, rs_pointC.Y, rs_pointC.Z])
            area = 0.5 * np.linalg.norm(np.cross(B - A, C - A))
            return area

        for c in support_combinations:
            supports_list = [supports[c[0]], supports[c[1]], supports[c[2]]]

            combined_distance = get_combined_distance_to_supports(supports_list)
            area = triangle_area(supports_list[0], supports_list[1], supports_list[2])
            if area == 0.0:
                score = combined_distance
            else:
                score = combined_distance / area
            score_per_combination[c] = score

        sorted_combinations = sorted(score_per_combination.items(), key=lambda item: item[1])

        support_combination = sorted_combinations[0][0]
        result_support = list(support_combination)
        for i in range(len(supports)):
            if i not in support_combination:
                result_support.append(i)
                break  # Add only one additional support if any

        return result_support

    def __check_if_door(self, support_nodes, load_node):
        support_points = [self.points[x] for x in support_nodes]
        load_point = self.points[load_node]
        combination = []

        def point_plane_distance(plane_pts, test_pt):
            A, B, C = plane_pts
            AB = B - A
            AC = C - A
            normal_vector = rg.Vector3d.CrossProduct(AB, AC)
            if normal_vector.IsZero:
                return 0.0
            normal_vector.Unitize()
            D = - (normal_vector.X * A.X + normal_vector.Y * A.Y + normal_vector.Z * A.Z)
            numerator = abs(normal_vector.X * test_pt.X + normal_vector.Y * test_pt.Y + normal_vector.Z * test_pt.Z + D)
            distance = numerator  # Since normal_vector is unitized, denominator is 1
            return distance

        def distance_to_centroid(pts, test_pt):
            centroid = rg.Point3d((pts[0].X + pts[1].X + pts[2].X) / 3,
                                  (pts[0].Y + pts[1].Y + pts[2].Y) / 3,
                                  (pts[0].Z + pts[1].Z + pts[2].Z) / 3)
            distance = (test_pt - centroid).Length
            return distance

        def is_door(three_supports, load_point, span_height_ratio=0.25):
            distance = point_plane_distance(three_supports, load_point)
            effective_span = distance_to_centroid(three_supports, load_point)
            if effective_span == 0:
                return False
            ratio = distance / effective_span
            return ratio <= span_height_ratio

        first_three = support_points[:3]
        if not is_door(first_three, load_point):
            return support_points
        else:
            for comb in combinations(support_points, 3):
                if not is_door(list(comb), load_point):
                    combination.extend(list(comb))
                    missing = [x for x in support_points if x not in list(comb)]
                    if missing:
                        combination.extend(missing)
                    return combination
            return True

    def assemble(self):
        graph = self.graph
        points = self.points
        assembly_steps = self.assembly_steps

        while True:
            if len(self.processed_nodes) == 0:
                first_supports, first_neighbour = self.__get_first_move()
                lines_to_add = []

                for support in first_supports:
                    p1 = points[support]
                    p2 = points[first_neighbour]
                    line = rg.LineCurve(p1, p2)
                    lines_to_add.append(line)

                missing_edges = self.__check_missing_edges(first_supports)
                for missing_edge in missing_edges:
                    p1 = points[missing_edge[0]]
                    p2 = points[missing_edge[1]]
                    line = rg.LineCurve(p1, p2)
                    lines_to_add.append(line)

                path = GH_Path(0)
                assembly_steps.AddRange(lines_to_add, path)

            elif len(self.processed_nodes) < len(points):
                non_rigid_candidates = self.__find_unprocessed_neighbors_subgraphs()
                rigid_candidates = [candidate for candidate in non_rigid_candidates if self.__can_node_be_rigid(candidate)]
                sorted_rigid_candidates = self.__sort_rigid_candidates(rigid_candidates)

                for candidate in sorted_rigid_candidates:
                    lines_to_add = []
                    nodes_to_connect_to = self.__get_possible_connections(candidate)
                    supports = [points[x] for x in nodes_to_connect_to]
                    nodes_sorted_indices = self.__get_sorted_supports(points[candidate], supports)
                    sorted_support_nodes = [nodes_to_connect_to[x] for x in nodes_sorted_indices]

                    door_check = self.__check_if_door(sorted_support_nodes, candidate)
                    if door_check == True:
                        continue
                    else:
                        sorted_support_points = door_check

                    for point in sorted_support_points:
                        line = rg.LineCurve(points[candidate], point)
                        lines_to_add.append(line)

                    self.processed_nodes.append(candidate)
                    path = GH_Path(assembly_steps.BranchCount)
                    assembly_steps.AddRange(lines_to_add, path)
                    break  # Proceed to the next candidate
                else:
                    return assembly_steps  # No valid candidates found; exit the loop
            else:
                return assembly_steps  # All nodes have been processed

# Instantiate the class with your inputs
my_truss = Trussemble(in_lines, in_rigid_points, in_start_point)
assembly_steps = my_truss.assemble()
processed_nodes = my_truss.processed_nodes
nodes = my_truss.points
processed_points = nodes
ordered_nodes = processed_points
