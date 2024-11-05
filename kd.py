from __future__ import annotations
import json
import math
import statistics
from typing import List

# Datum class.
# DO NOT MODIFY.
class Datum():
    def __init__(self,
                 coords : tuple[int],
                 code   : str):
        self.coords = coords
        self.code   = code
    def to_json(self) -> str:
        dict_repr = {'code':self.code,'coords':self.coords}
        return(dict_repr)

# Internal node class.
# DO NOT MODIFY.
class NodeInternal():
    def  __init__(self,
                  splitindex : int,
                  splitvalue : float,
                  leftchild,
                  rightchild):
        self.splitindex = splitindex
        self.splitvalue = splitvalue
        self.leftchild  = leftchild
        self.rightchild = rightchild

# Leaf node class.
# DO NOT MODIFY.
class NodeLeaf():
    def  __init__(self,
                  data : List[Datum]):
        self.data = data

# KD tree class.
class KDtree():
    def  __init__(self,
                  splitmethod : str,
                  k           : int,
                  m           : int,
                  root        : NodeLeaf = None):
        self.k    = k
        self.m    = m
        self.splitmethod = splitmethod
        self.root = root

    # For the tree rooted at root, dump the tree to stringified JSON object and return.
    # DO NOT MODIFY.
    def dump(self) -> str:
        def _to_dict(node) -> dict:
            if isinstance(node,NodeLeaf):
                return {
                    "p": str([{'coords': datum.coords,'code': datum.code} for datum in node.data])
                }
            else:
                return {
                    "splitindex": node.splitindex,
                    "splitvalue": node.splitvalue,
                    "l": (_to_dict(node.leftchild)  if node.leftchild  is not None else None),
                    "r": (_to_dict(node.rightchild) if node.rightchild is not None else None)
                }
        if self.root is None:
            dict_repr = {}
        else:
            dict_repr = _to_dict(self.root)
        return json.dumps(dict_repr,indent=2)

    # Insert the Datum with the given code and coords into the tree.
    # The Datum with the given coords is guaranteed to not be in the tree.
    def insert(self,point:tuple[int],code:str):

        # if root is none, set root to a nodeLeaf w/ datum in it!
        if self.root is None:
            self.root = NodeLeaf(data=[Datum(coords=point, code=code)])
            return

        # if root is NodeLeaf, insert into root node then check if bad
        if isinstance(self.root, NodeLeaf):
            curr = self.root
            curr.data.append(Datum(coords=point, code=code))
        # root is not leaf, go searching for home!
        else:
            curr = self.root
            while not isinstance(curr, NodeLeaf):
                if point[curr.splitindex] < curr.splitvalue:
                    parent = curr
                    curr = curr.leftchild
                else:
                    parent = curr
                    curr = curr.rightchild
                
            # now, add to curr!
            curr.data.append(Datum(coords=point, code=code))


        # data has definitely been added atp, now let's handle some splitting!!
        if len(curr.data) > self.m:
            # check what the split method is then treat accordingly

            # spreaders ftw
            if self.splitmethod == "spread":
                # make list to track spreads
                spread_lst = [None] * self.k

                # find spread for each idx of k
                for i in range(self.k):
                    # sort list by values of 
                    lst = sorted(curr.data, key=lambda datum: datum.coords[i])

                    # add spread to the spread_lst
                    high = lst[-1]
                    low = lst[0]
                    spread_lst[i] = high.coords[i] - low.coords[i]

                # find the max spread and use that as new_split
                new_index = 0
                for i in range(1, len(spread_lst)):
                    if spread_lst[i] > spread_lst[new_index]:
                        new_index = i  # Update index if a larger element is found

                # now that new_split is found, we just need splitVal and to sort/split the list!!
                temp = curr


                splitVal = []
                # find splitval for internal node:
                for i in temp.data:
                    splitVal.append(i.coords[new_index])

                # find median
                splitVal = float(statistics.median(splitVal))

                # sort list of data
                sorted_data = sorted(temp.data, key=lambda datum: datum.coords[new_index])
                midpoint = len(sorted_data) // 2
    
                # Split the list into two halves
                left = sorted_data[:midpoint]
                right = sorted_data[midpoint:]

                # make the nodes for left and right sides of root
                left_node = NodeLeaf(data=left)
                right_node = NodeLeaf(data=right)

                # create new node and add onto parent node where it needs to go!

                # curr was root; split root and set the internal node to be self.root
                if curr is self.root:
                    self.root = NodeInternal(splitindex=new_index, splitvalue=splitVal, leftchild=left_node, rightchild=right_node)
                
                # curr is not the root, so we need to check which side of parent to put it on
                elif curr is parent.leftchild:
                    parent.leftchild = NodeInternal(splitindex=new_index, splitvalue=splitVal, leftchild=left_node, rightchild=right_node)
                elif curr is parent.rightchild:
                    parent.rightchild = NodeInternal(splitindex=new_index, splitvalue=splitVal, leftchild=left_node, rightchild=right_node)
                return

            # method is split; let's go bananas
            if self.splitmethod == "cycle":
                # if the root is a leaf node, make it the child of a nodeInternal
                if isinstance(self.root, NodeLeaf):
                    temp = self.root
                    
                    splitVal = []
                    # find splitval for internal node:
                    for i in temp.data:
                        splitVal.append(i.coords[0])

                    # find median
                    splitVal = float(statistics.median(splitVal))

                    # sort list of data

                    sorted_data = sorted(temp.data, key=lambda datum: datum.coords[0])
                    midpoint = len(sorted_data) // 2
        
                    # Split the list into two halves
                    left = sorted_data[:midpoint]
                    right = sorted_data[midpoint:]

                    # make the nodes for left and right sides of root
                    left_node = NodeLeaf(data=left)
                    right_node = NodeLeaf(data=right)

                    self.root = NodeInternal(splitindex=0, splitvalue=splitVal, leftchild=left_node, rightchild=right_node)
                    return
                
                # the root is not a leaf node, so curr is some random node getting split:
                # check splitindex and split on the next index mod k
                new_index = (parent.splitindex + 1) % self.k

                temp = curr

                splitVal = []
                # find splitval for internal node:
                for i in temp.data:
                    splitVal.append(i.coords[new_index])

                # find median
                splitVal = float(statistics.median(splitVal))

                # sort list of data
                sorted_data = sorted(temp.data, key=lambda datum: datum.coords[new_index])
                midpoint = len(sorted_data) // 2
    
                # Split the list into two halves
                left = sorted_data[:midpoint]
                right = sorted_data[midpoint:]

                # make the nodes for left and right sides of root
                left_node = NodeLeaf(data=left)
                right_node = NodeLeaf(data=right)

                # create new node and add onto parent node where it needs to go!
                if curr is parent.leftchild:
                    parent.leftchild = NodeInternal(splitindex=new_index, splitvalue=splitVal, leftchild=left_node, rightchild=right_node)
                elif curr is parent.rightchild:
                    parent.rightchild = NodeInternal(splitindex=new_index, splitvalue=splitVal, leftchild=left_node, rightchild=right_node)
                return


        # no need to split, return!       
        else: return
                


    # END INSERT

    # Delete the Datum with the given point from the tree.
    # The Datum with the given point is guaranteed to be in the tree.
    def delete(self,point:tuple[int]):
        curr = self.root

        if isinstance(curr, NodeLeaf):
            for i in range(len(curr.data)):
                if curr.data[i].coords == point:
                    del curr.data[i]  # Remove the datum at index i
                    break
        
        else:

            prev_parent = None
            parent = None
            # root wasn't a leaf, let's keep looking:
            # compare point coords to splitvals until leaf reached
            while not isinstance(curr, NodeLeaf):
                if point[curr.splitindex] < curr.splitvalue:
                    prev_parent = parent
                    parent = curr
                    curr = curr.leftchild
                else:
                    prev_parent = parent                    
                    parent = curr
                    curr = curr.rightchild

            # curr is now the leaf; search that mf
            for i in range(len(curr.data)):
                if curr.data[i].coords == point:
                    del curr.data[i]  # Remove the datum at index i
                    break
                
        if curr.data == []:
            if self.root == curr:
                self.root = None
                return
            
            # if the node above was the root, make the other leaf the root
            if prev_parent is None:
                if curr is parent.leftchild:
                    self.root = parent.rightchild
                    return
                if curr is parent.rightchild:
                    self.root = parent.leftchild
                    return
            

            if curr is parent.leftchild:
                if parent is prev_parent.leftchild:
                    prev_parent.leftchild = parent.rightchild
                else:
                    prev_parent.rightchild = parent.rightchild
            if curr is parent.rightchild:
                if parent is prev_parent.leftchild:
                    prev_parent.leftchild = parent.leftchild
                else:
                    prev_parent.rightchild = parent.leftchild


    # END DELETE

    # Find the k nearest neighbors to the point.
    def knn(self,k:int,point:tuple[int]) -> str:
        # Use the strategy discussed in class and in the notes.
        # The list should be a list of elements of type Datum.
        # While recursing, count the number of leaf nodes visited while you construct the list.
        # The following lines should be replaced by code that does the job.
        leaveschecked = 0
        knnlist = [(None, None)] * k

        # recursive function defined to start at root and continue downwards
        # until the list is full of good data and only valid leaves have been visited
        # by comparing the point to the bounding boxes.
        def knn_rec(node, point:tuple[int], knnlist:List[(Datum, int)]) -> List[(Datum, int)]:

            nonlocal leaveschecked

            # helper function for finding the distance between a point and a piont/bounding box
            def dist(point1:tuple[int], point2:tuple[int], box:List[tuple[int]]) -> int:
                # no box given; calculate distance between two points and return int
                if box is None:
                    distance = 0
                    temp = 0
                    for i in range(len(point1)):
                        temp = point1[i] - point2[i]
                        distance += temp * temp

                    return distance
                
                # no second point given; calculate distance
                # between point and box and return int
                if point2 is None:
                    distance = 0
                    temp = 0
                    # for each dimension:
                    for i in range(len(point1)):
                        # check if min or max to calculate with
                        if  point1[i] < box[i][0]:
                            temp = box[i][0] - point1[i]
                        elif point1[i] > box[i][1]:
                            temp = point1[i] - box[i][1]
                        else:
                            temp = 0

                        distance += temp * temp

                    return distance

                else:
                    print("incorrect usage of dist function; be less stupid")

            # Used to find the maximum and minimum values of each dimension
            # so that d^2 values can be found
            def traverse_and_find_extremes(node, dimension_index:int):
                # Helper function to perform depth-first search 
                def dfs(node):
                    nonlocal min_val, max_val
                    if isinstance(node, NodeLeaf):
                        # Leaf node reached, update min_val and max_val with the coordinates
                        for datum in node.data:
                            value = datum.coords[dimension_index]
                            min_val = min(min_val, value)
                            max_val = max(max_val, value)
                    else:
                        # Internal node, recursively explore left and right children
                        dfs(node.leftchild)
                        dfs(node.rightchild)

                # Initialize min_val and max_val to positive and negative infinity respectively
                min_val = float('inf')
                max_val = float('-inf')

                # Start DFS traversal from the root node
                if node:
                    dfs(node)

                return (min_val, max_val)
            
            # helper to check if list is full
            def full(lst) -> bool:
                for element in knnlist:
                    if element == (None, None):
                        full = False
                        return
                full = True

                return full
            
            # if passed in node is a NodeLeaf, check all the points to see if their d
            # 2 values are smaller than any of the points in our list and if they are,
            # replace the further points in our list with closer ones.
            if isinstance(node, NodeLeaf):

                # increment the leaveschecked variable to indicate that a leaf was visited
                leaveschecked += 1

                # if the list is not full, add the closest points to the search point
                # once list is full, replace the furthest point if considered point is closer
                # then, return the list after sorting it by closeness to point
                for datum in node.data:
                    # here, we check if the list is full.
                    # if list is not full, just add the element and it's not deep
                    if not full(knnlist):
                        for i in range(len(knnlist)):
                            if knnlist[i] == (None, None):
                                knnlist[i] = (datum, dist(point1=point, point2=datum.coords, box=None))
                                break


                    # if the list is full, iterate through the list and check if the considered point
                    # is closer than any point in the list. if it is, replace the furthest away one
                    # could be valid to make the list be like:
                    # List[(Datum, int)] to keep track of the distances?
                    else:
                        # first sort list so that the last element has the largest distance
                        knnlist = sorted(knnlist, key=lambda x: x[1])

                        dist_new = dist(point1=point, point2=datum.coords, box=None)
                        # compare dist of knnlist[-1][1] with dist from datum.coords
                        if dist_new < knnlist[-1][1]:
                            knnlist[-1] = (datum, dist_new)
                        if dist_new == knnlist[-1][1]:
                            if knnlist[-1][0].code > datum.code:
                                knnlist[-1] = (datum, dist_new)                          
                    # Iteration of for datum ended
                # for datum loop ended
                # return the new list!!!!
                return knnlist



            # if passed in node is a splitting node, and there are two subtrees to visit, visit the
            # subtree whose bounding box is closest to P first. check subtrees till list is full
            #
            # Then, if list full and bounding box of subtree is further away than all points,
            # do not go to subtree. If closer, then go in and check for closer points.
            if isinstance(node, NodeInternal):
                # find the bounding boxes for each subtree
                r_box = [None] * self.k
                l_box = [None] * self.k

                # loop through the dims in order to find the min/max for each dim
                # and put them into the lists of tuples above.
                for i in range(self.k):
                    r_box[i] = traverse_and_find_extremes(node=node.rightchild, dimension_index=i)
                    l_box[i] = traverse_and_find_extremes(node=node.leftchild, dimension_index=i)

                # now, the bounding boxes for each subtree are complete; let's do some
                # distance calculation after checking if the list is full or not

                r_dist = dist(point1=point, point2=None, box=r_box)
                l_dist = dist(point1=point, point2=None, box=l_box)

                # print("\n")
                # print("@ " + str(node.splitindex) + " = " + str(node.splitvalue))
                # print("left: " + str(l_dist))
                # print("right: " + str(r_dist))
                # print("Lbox: " + str(l_box))
                # print("Rbox: " + str(r_box))
                
                # if the list is not yet full, we need to traverse the subtrees to find some
                # stuff to fill the list with!
                if not full(knnlist):
                    # left box is closer, we go there first
                    if l_dist <= r_dist:
                        # print("going left")
                        # left calculations completed and sorted
                        nknnlist_left = knn_rec(node=node.leftchild, point=point, knnlist=knnlist)

                        # list is now full so we might not need to go into right
                        if full(nknnlist_left):
                            nknnlist_left = sorted(nknnlist_left, key=lambda x: x[1])


                            # print("left full@ " + str(node.splitindex) + " = " + str(node.splitvalue))
                            if nknnlist_left[-1][1] >= r_dist:
                                # print("checking right@ " + str(node.splitindex) + " = " + str(node.splitvalue))
                                nknnlist_both = knn_rec(node=node.rightchild, point=point, knnlist=nknnlist_left)
                            else:
                                return nknnlist_left
                        
                        else:
                            nknnlist_both = knn_rec(node=node.rightchild, point=point, knnlist=nknnlist_left)
                    
                    # right box is closer, we go there first
                    else:
                        # print("going right")
                        # right calculations completed and sorted
                        nknnlist_right = knn_rec(node=node.rightchild, point=point, knnlist=knnlist)

                        if full(nknnlist_right):
                            nknnlist_right = sorted(nknnlist_right, key=lambda x: x[1])


                            # print("right full@ " + str(node.splitindex) + " = " + str(node.splitvalue))
                            if nknnlist_right[-1][1] >= l_dist:
                                # print("checking left@ " + str(node.splitindex) + " = " + str(node.splitvalue))
                                nknnlist_both = knn_rec(node=node.leftchild, point=point, knnlist=nknnlist_right)
                            else:
                                return nknnlist_right
                        else:
                            nknnlist_both = knn_rec(node=node.leftchild, point=point, knnlist=nknnlist_right)

                    # now, return knnlist_both which has to be created
                    # by one of the cases if no return happened lmao
                    return nknnlist_both

                #list is full; let's compare the distances of:
                # a: point->furthest in list
                # b: point-> l_box
                # c: point -> r_box
                # 
                # x1: a > b
                # x2: a > c
                # if x1 && x2: check l and r, whichever closer first
                # if x1 xor x2: check l or r, whichever closer
                # if ~x1 && ~x2, do not change tree and return list!
                if full(knnlist):
                    knnlist = sorted(knnlist, key=lambda x: x[1])
                    furthest = knnlist[-1][1]

                    x1 = furthest >= l_dist
                    x2 = furthest >= r_dist


                    # furthest point is further than both box
                    if x1 and x2:
                        # check which box to go to first

                        if l_dist < r_dist:
                            # check left subtree!
                            knnlist_left = knn_rec(node=node.leftchild, point=point, knnlist=knnlist)
                            knnlist_left = sorted(knnlist_left, key=lambda x: x[1])

                            # if furthest is still further than other subtree, continue to check other subtree
                            if knnlist_left[-1][1] > r_dist:
                                knnlist_both = knn_rec(node=node.rightchild, point=point, knnlist=knnlist_left)
                            else: return knnlist_left
                        else:
                            knnlist_right = knn_rec(node=node.rightchild, point=point, knnlist=knnlist)
                            knnlist_right = sorted(knnlist_right, key=lambda x: x[1])

                            if knnlist_right[-1][1] > l_dist:
                                knnlist_both = knn_rec(node=node.leftchild, point=point, knnlist=knnlist_right)
                            else: return knnlist_right

                        # now, return knnlist_both which has to be created by one of the cases lmao
                        return knnlist_both
                    
                    # only one of them is closer; we only need to check one branch
                    if x1 ^ x2:
                        # left clsoer
                        if x1:
                            knnlist_left = knn_rec(node=node.leftchild, point=point, knnlist=knnlist)
                            knnlist_left = sorted(knnlist_left, key=lambda x: x[1])
                            return knnlist_left
                        
                        # right clsoer
                        else:
                            knnlist_right = knn_rec(node=node.rightchild, point=point, knnlist=knnlist)
                            knnlist_right = sorted(knnlist_right, key=lambda x: x[1])
                            return knnlist_right

                    # both are further: no need to check these subtrees at all lmao
                    if not x1 and not x2:
                        return knnlist

        knn_with_dists = knn_rec(node=self.root, point=point, knnlist=knnlist)

        knnlist = [datum for datum, _ in knn_with_dists]

        # The following return line can probably be left alone unless you make changes in variable names.
        return(json.dumps({"leaveschecked":leaveschecked,"points":[datum.to_json() for datum in knnlist]},indent=2))