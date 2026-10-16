variable "aws_region" {
  description = "AWS region for the Petal Shop infrastructure."
  type        = string
  default     = "ap-south-1"
}

variable "cluster_name" {
  description = "Name of the EKS cluster."
  type        = string
  default     = "petal-shop-cluster"
}

variable "node_instance_type" {
  description = "EC2 instance type for the worker nodes (t3.micro is free tier)."
  type        = string
  default     = "t3.micro"
}
