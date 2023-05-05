import csv
import math
import sys
import kinetic_loss
import matplotlib.pyplot as plt

max_frame_cut = 20

landmark_names = ["nose", "right shoulder", "left shoulder", "right elbow", "left elbow",
"right wrist", "left wrist", "right hip", "left hip", "right knee", "left knee", 
"right ankle", "left ankle"]

#Pairs of angles that need to be measured with the joint that should be moved to adjust them to minimize collateral changes
angle_point_pairs = {"left elbow" : "left wrist", "right elbow": "right wrist", "left armpit": "left elbow", "right armpit" : "right elbow",
"left shoulder":"left hip", "left hip": "right hip", "right hip": "right shoulder", "right shoulder": "left shoulder"}

limb_names = {"shoulders": ["left shoulder", "right shoulder"], "left oblique": ["left shoulder", "left hip"], "right oblique": ["right shoulder", "right hip"],
"hips": ["left hip", "right hip"], "right upper arm": ["right shoulder", "right elbow"], "left upper arm": ["left shoulder", "left elbow"],
"right forearm": ["right elbow", "right wrist"], "left forearm": ["left elbow", "left wrist"], "right thigh": ["right hip", "right knee"],
"left thigh": ["left hip", "left knee"], "right shin": ["right knee", "right ankle"], "left shin": ["left knee", "left ankle"]}

#Pairs of angles and their component joints, with the joint to adjust for that angle being the last in the list
angle_joint_groupings = {"left elbow" : ["left shoulder", "left elbow", "left wrist"], "right elbow": ["right shoulder", "right elbow", "right wrist"],
 "left armpit": ["left hip", "left shoulder", "left elbow"], "right armpit" : ["right hip", "right shoulder", "right elbow"],
"left shoulder":["right shoulder","left shoulder", "left hip"], "left hip": ["left shoulder", "left hip", "right hip"], 
"right hip": ["left hip", "right hip", "right shoulder"], "right shoulder": ["right hip", "right shoulder", "left shoulder"]}

bones = {}

base_skeleton_file = "output_skeleton_base.csv"

target_skeleton_file = "output_skeleton_target.csv"


class Skeleton_Frame():

	def __init__(self):
		self.landmark_names = ["nose", "right shoulder", "left shoulder", "right elbow", "left elbow",
"right wrist", "left wrist", "right hip", "left hip", "right knee", "left knee", 
"right ankle", "left ankle"]
		self.landmarks = {}
		for landmark in self.landmark_names:
			self.landmarks[landmark] = [0,0,0,0] #{'x': 0, 'y': 0, 'z': 0, 'v': 0} consider for readability
		self.angles = {}
		for angle in angle_joint_groupings.keys():
			self.angles[angle] = 0
		self.limbs = {}
		for limb in limb_names.keys():
			self.limbs[limb] = 0
		self.centroid = (0,0)
		
	def set_specific(self, landmark_name, landmark):
		self.landmarks[landmark_name] = landmark

	def set_all(self, landmarks):
		for key in landmarks.keys():
			self.set_specific(key, landmarks[key])
		self.calculate_angles()
		self.calculate_limb_length()
		self.calculate_centroid()

	def calculate_angles(self):
		for angle in angle_joint_groupings.keys():
			target_joints = angle_joint_groupings[angle]
			# print(target_joints[0])
			joint_values = [self.landmarks[target_joints[0]],self.landmarks[target_joints[1]],self.landmarks[target_joints[2]]]
			# sys.exit()
			new_angle = self.calculate_angle(joint_values[0], joint_values[1], joint_values[2]) 
			self.angles[angle] = new_angle


	def calculate_limb_length(self):
		for limb in self.limbs.keys():
			joints  = limb_names[limb]
			limb_length = math.sqrt(abs(self.landmarks[joints[0]][0] - self.landmarks[joints[1]][0]) + abs(self.landmarks[joints[0]][1] - self.landmarks[joints[1]][1]))
			self.limbs[limb] = limb_length

	def calculate_angle(self, x,y,z):
		v1 = [x[0] - y[0],x[1] - y[1],x[2] - y[2]]
		v2 = [z[0] - y[0],z[1] - y[1],z[2] - y[2]]
		# m1 = abs(sum(v1[:-1]))
		m1 = 0 
		for value in v1:
			m1 += abs(value)
		m2 = 0
		for value in v2:
			m2 += abs(value)
		# print(v1)
		# print(v2)
		# print((math.acos(self.dot(v1,v2)/(m1*m2)) *180)/math.pi)
		return math.acos(self.dot(v1,v2)/(m1*m2))

	def calculate_centroid(self):
		x = []
		y = []
		for landmark in self.landmarks.keys():
			# print(self.landmarks[landmark][0])
			x.append(self.landmarks[landmark][0])
			y.append(self.landmarks[landmark][1])
		self.centroid = ((sum(x)/len(x)),(sum(y)/len(y)))


	def dot(self, v1, v2):
		return (v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2])




class Actor():
	def __init__(self):
		self.frames = []

		self.average_lengths = {}

	def add_frame(self, frame):
		self.frames.append(frame)
		self.calculate_average_lengths()

	def calculate_average_lengths(self):
		sum_lengths = {}
		for frame in self.frames:
			frame_limbs = frame.limbs
			for limb in frame_limbs.keys():
				try:
					sum_lengths[limb].append(frame_limbs[limb])
				except:
					sum_lengths[limb] = [frame_limbs[limb]]
		for limb in sum_lengths:
			self.average_lengths[limb] = sum(sum_lengths[limb])/len(sum_lengths[limb])




with open(base_skeleton_file, 'r') as f:
	base_actor = Actor()
	file_reader = csv.reader(f)
	#skip heading
	file_reader.__next__()
	line = file_reader.__next__()
	i = 0
	frame_landmarks = {}
	while not line == "":
		line = line [1:-1]

		for i in range(len(line)):
			if i % 4 == 0:
				if i > 0:
					frame_landmarks[landmark_names[(i//4)-1]] = current_landmark	
				current_landmark = []				
			current_landmark.append(float(line[i]))
		new_frame = Skeleton_Frame()
		new_frame.set_all(frame_landmarks)
		base_actor.add_frame(new_frame)
		try:
			line = file_reader.__next__()
		except:
			break
	f.close()


with open(target_skeleton_file, 'r') as f:
	target_actor = Actor()
	target_file_reader = csv.reader(f)
	#skip heading
	target_file_reader.__next__()
	line = target_file_reader.__next__()
	i = 0
	frame_landmarks = {}
	while not line == "":
		line = line [1:-1]
		for i in range(len(line)):
			if i % 4 == 0:
				if i > 0:
					frame_landmarks[landmark_names[(i//4)-1]] = current_landmark	
				current_landmark = []				
			current_landmark.append(float(line[i]))
		new_target_frame = Skeleton_Frame()
		new_target_frame.set_all(frame_landmarks)
		target_actor.add_frame(new_target_frame)
		print(new_target_frame is new_frame)
		try:
			line = target_file_reader.__next__()
		except:
			break


min_frames = min(len(target_actor.frames), len(base_actor.frames))



x = [i for i in range(min_frames)]


min_sum_total_loss = 9999999999999999
max_sum_total_loss = 0
offset = 0
max_offset = 0

differential = max(len(target_actor.frames) - min_frames, len(base_actor.frames) - min_frames)

loss_graphs = []
offset_total_losses = []

for i in range(differential + max_frame_cut):
	total_loss_values = []
	for j in range(min_frames - max(0,(i - differential))):
		if len(base_actor.frames) > len(target_actor.frames):
			total_loss_values.append(kinetic_loss.kinetic_loss(base_actor.frames[j + i], target_actor.frames[j + max(0, i - differential)])['total'])
		else:
			total_loss_values.append(kinetic_loss.kinetic_loss(base_actor.frames[j + max(0, i - differential)], target_actor.frames[j + i])['total'])
	loss_graphs.append(total_loss_values)
	sum_total_loss = sum(total_loss_values)
	offset_total_losses.append(sum_total_loss)

	if sum_total_loss/len(total_loss_values) < min_sum_total_loss:
		min_sum_total_loss = sum_total_loss/len(total_loss_values)
		offset = i
	if sum_total_loss/len(total_loss_values) > max_sum_total_loss:
		max_sum_total_loss = sum_total_loss/len(total_loss_values)
		max_offset = i


print("optimal offset: {}".format(offset))
print("differential: {}".format( differential))
print("worst offset in range: {}".format(max_offset))
print(len(loss_graphs))
label = "optimal sync: {} frames".format(offset)
label2 = "random sync: {} frames".format(5)
label3 = "worst sync: {} frames".format(max_offset)
x1 = [i for i in range(len(loss_graphs[offset]))]
x2 = [i for i in range(len(loss_graphs[5]))]
x3 = [i for i in range(len(loss_graphs[max_offset]))]
plt.plot(x1,loss_graphs[offset], label=label)
plt.plot(x2,loss_graphs[5], label=label2)
plt.plot(x3,loss_graphs[max_offset], label=label3)
plt.legend()
plt.show()


total_loss_values = []
left_arm_loss_values = []
right_arm_loss_values = []
left_leg_loss_values = []
right_leg_loss_values = []
torso_loss_values = []
upper_body_loss_values = []
lower_body_loss_values = []
left_side_loss_values = []
right_side_loss_values = []

if len(base_actor.frames) > len(target_actor.frames):
	for i in range(min_frames):
		total_loss_values.append(kinetic_loss.kinetic_loss(base_actor.frames[i + offset], target_actor.frames[i])['total'])
		left_arm_loss_values.append(kinetic_loss.kinetic_loss(base_actor.frames[i + offset], target_actor.frames[i])['left arm'])
		right_arm_loss_values.append(kinetic_loss.kinetic_loss(base_actor.frames[i + offset], target_actor.frames[i])['right arm'])
		left_leg_loss_values.append(kinetic_loss.kinetic_loss(base_actor.frames[i + offset], target_actor.frames[i])['left leg'])
		right_leg_loss_values.append(kinetic_loss.kinetic_loss(base_actor.frames[i + offset], target_actor.frames[i])['right leg'])
		torso_loss_values.append(kinetic_loss.kinetic_loss(base_actor.frames[i + offset], target_actor.frames[i])['torso'])
		upper_body_loss_values.append(kinetic_loss.kinetic_loss(base_actor.frames[i + offset], target_actor.frames[i])['upper body'])
		lower_body_loss_values.append(kinetic_loss.kinetic_loss(base_actor.frames[i + offset], target_actor.frames[i])['lower body'])
		left_side_loss_values.append(kinetic_loss.kinetic_loss(base_actor.frames[i + offset], target_actor.frames[i])['left side'])
		right_side_loss_values.append(kinetic_loss.kinetic_loss(base_actor.frames[i + offset], target_actor.frames[i])['right side'])
else:
	for i in range(min_frames):
		total_loss_values.append(kinetic_loss.kinetic_loss(base_actor.frames[i], target_actor.frames[i + offset])['total'])
		left_arm_loss_values.append(kinetic_loss.kinetic_loss(base_actor.frames[i], target_actor.frames[i + offset])['left arm'])
		right_arm_loss_values.append(kinetic_loss.kinetic_loss(base_actor.frames[i], target_actor.frames[i + offset])['right arm'])
		left_leg_loss_values.append(kinetic_loss.kinetic_loss(base_actor.frames[i], target_actor.frames[i + offset])['left leg'])
		right_leg_loss_values.append(kinetic_loss.kinetic_loss(base_actor.frames[i], target_actor.frames[i + offset])['right leg'])
		torso_loss_values.append(kinetic_loss.kinetic_loss(base_actor.frames[i], target_actor.frames[i + offset])['torso'])
		upper_body_loss_values.append(kinetic_loss.kinetic_loss(base_actor.frames[i], target_actor.frames[i + offset])['upper body'])
		lower_body_loss_values.append(kinetic_loss.kinetic_loss(base_actor.frames[i], target_actor.frames[i + offset])['lower body'])
		left_side_loss_values.append(kinetic_loss.kinetic_loss(base_actor.frames[i], target_actor.frames[i + offset])['left side'])
		right_side_loss_values.append(kinetic_loss.kinetic_loss(base_actor.frames[i], target_actor.frames[i + offset])['right side'])

plt.plot(x,total_loss_values, label="Total")
plt.plot(x, upper_body_loss_values, label="upper body")
plt.plot(x, lower_body_loss_values, label="lower body")
plt.plot(x, torso_loss_values, label = "torso")
plt.legend()
plt.show()

