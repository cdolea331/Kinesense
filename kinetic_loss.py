import math

loss_groups = {"left arm": ["left shoulder", "left elbow", "left wrist"], "right arm": ["right shoulder", "right elbow", "right wrist"],
"left leg": ["left hip", "left knee", "left ankle"], "right leg": ["right hip", "right knee", "right ankle"], 
"upper body": ["left shoulder", "left elbow", "left wrist", "right shoulder", "right elbow", "right wrist"], 
"lower body": ["left hip", "left knee", "left ankle", "right hip", "right knee", "right ankle"], 
"torso": ["left shoulder", "right shoulder", "left hip", "right hip"], "right side": ["right shoulder", "right elbow", "right wrist", "right hip", "right knee", "right ankle"],
"left side": ["left shoulder", "left elbow", "left wrist", "left hip", "left knee", "left ankle"],
"total": ["left shoulder", "left elbow", "left wrist", "left hip", "left knee", "left ankle", "right shoulder", "right elbow", "right wrist", "right hip", "right knee", "right ankle"]}


def euclidean_distance(x1, x2):
	return(math.sqrt(sum([(x[0] - x[1])**2 for x in zip(x1, x2)])))

def wing_loss( x1, x2, w = 5, epsilon = 4):
	C = w - (w * math.log(1 + w/epsilon) )
	distance = euclidean_distance(x1,x2)
	return math.log(1 + abs(distance/epsilon)) if abs(distance) < w else abs(distance) - C
	
def smooth_l1_loss(x1, x2):
	distance = euclidean_distance(x1,x2)
	return (distance ** 2)/2 if abs(distance) < 1 else abs(distance) - 0.5

def l2_loss(x1, x2):
	return (euclidean_distance(x1, x2)) ** 2




landmark_tiers = {"nose" : 1, "right shoulder" : 0, "left shoulder" : 0, "right hip" : 0, "left hip" : 0,
"nose": 1, "left elbow": 1, "right elbow": 1, "left knee": 1, "right knee": 1, 
"right wrist": 2, "left wrist": 2, "right ankle": 2, "left ankle": 2}

loss_function_tiers = [wing_loss, smooth_l1_loss, l2_loss]

def kinetic_loss(base_skeleton, target_skeleton):
	losses  = {}
	for loss_group in loss_groups.keys():
		losses[loss_group] = 0

	for landmark_name in base_skeleton.landmarks.keys():
		landmark_loss = loss_function_tiers[landmark_tiers[landmark_name]](base_skeleton.landmarks[landmark_name][:2], target_skeleton.landmarks[landmark_name][:2])
		for loss in losses.keys():
			if landmark_name in loss_groups[loss]:
				losses[loss] += landmark_loss
	return losses

