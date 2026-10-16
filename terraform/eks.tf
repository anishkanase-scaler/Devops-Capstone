# IAM role for the EKS control plane
resource "aws_iam_role" "cluster" {
  name = "petal-shop-eks-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "eks.amazonaws.com" }
    }]
  })

  tags = {
    Name      = "petal-shop-eks-cluster-role"
    Project   = "petal-shop"
    ManagedBy = "Terraform"
  }
}

resource "aws_iam_role_policy_attachment" "cluster_policy" {
  role       = aws_iam_role.cluster.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

resource "aws_eks_cluster" "main" {
  name     = var.cluster_name
  role_arn = aws_iam_role.cluster.arn

  vpc_config {
    subnet_ids = [aws_subnet.public_a.id, aws_subnet.public_b.id]
  }

  # Lets whoever runs terraform use kubectl on the cluster straight away
  access_config {
    authentication_mode                         = "API_AND_CONFIG_MAP"
    bootstrap_cluster_creator_admin_permissions = true
  }

  tags = {
    Name      = var.cluster_name
    Project   = "petal-shop"
    ManagedBy = "Terraform"
  }

  depends_on = [aws_iam_role_policy_attachment.cluster_policy]
}

# IAM role for the worker nodes
resource "aws_iam_role" "node" {
  name = "petal-shop-eks-node-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })

  tags = {
    Name      = "petal-shop-eks-node-role"
    Project   = "petal-shop"
    ManagedBy = "Terraform"
  }
}

resource "aws_iam_role_policy_attachment" "node_worker" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}

resource "aws_iam_role_policy_attachment" "node_cni" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}

resource "aws_iam_role_policy_attachment" "node_ecr" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "petal-shop-nodes"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = [aws_subnet.public_a.id, aws_subnet.public_b.id]

  instance_types = [var.node_instance_type]
  disk_size      = 20 # GiB; the free tier includes 30 GiB of EBS in total

  scaling_config {
    desired_size = 2
    min_size     = 1
    max_size     = 2
  }

  tags = {
    Name      = "petal-shop-nodes"
    Project   = "petal-shop"
    ManagedBy = "Terraform"
  }

  depends_on = [
    aws_iam_role_policy_attachment.node_worker,
    aws_iam_role_policy_attachment.node_cni,
    aws_iam_role_policy_attachment.node_ecr,
  ]
}
