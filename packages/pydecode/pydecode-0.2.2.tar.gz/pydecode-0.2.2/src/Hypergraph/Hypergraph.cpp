// Copyright [2013] Alexander Rush

#include <typeinfo>
#include <vector>

#include "Hypergraph/Hypergraph.hh"

int Hypergraph::ID = 0;

HEdge Hypergraph::add_edge(const vector<HNode> &nodes)  {
    if (unary_) {
        return add_edge(nodes[0]);
    }
    assert(lock_);
    assert(!unary_);

    HEdge edge = temp_structure_->edges_.size();
    temp_structure_->edges_.push_back(edge);
    temp_structure_->edge_tails_.push_back(nodes);
    temp_structure_->edge_heads_.push_back(creating_node_);
    foreach (HNode node, nodes) {
        if (node == NODE_NULL) {
            throw HypergraphException("Hypernode is NULL.");
        }
    }
    return edge;
}

HEdge Hypergraph::add_edge(HNode node)  {
    assert(lock_);
    assert(unary_);

    HEdge edge = temp_structure_->edges_.size();
    temp_structure_->edges_.push_back(edge);
    temp_structure_->edge_tails_unary_.push_back(node);
    temp_structure_->edge_heads_.push_back(creating_node_);
    return edge;
}

HNode Hypergraph::start_node() {
    terminal_lock_ = false;
    lock_ = true;
    // creating_node_ = new Hypernode();
    // creating_node_->set_id(temp_structure_->nodes_.size());
    creating_node_ = temp_structure_->nodes_.size();
    temp_structure_->nodes_.push_back(creating_node_);
    return creating_node_;
}

bool Hypergraph::end_node() {
    assert(lock_);
    lock_ = false;

    // Remove this node if it has no edges.
    if (temp_structure_->edges_.size() > 0 &&
        temp_structure_->edge_heads_.back() == creating_node_) {
        return true;
    } else {
        // creating_node_->set_id(-1);
        temp_structure_->nodes_.pop_back();
        return false;
    }
}

HNode Hypergraph::add_terminal_node() {
    assert(terminal_lock_);
    // Hypernode *node = new Hypernode();
    // node->set_id(temp_structure_->nodes_.size());

    HNode node = temp_structure_->nodes_.size();
    temp_structure_->nodes_.push_back(node);
    return temp_structure_->nodes_[temp_structure_->nodes_.size() - 1];
}

void Hypergraph::fill() {
    vector<bool> reachable_nodes(temp_structure_->nodes_.size(), false);
    vector<bool> reachable_edges(temp_structure_->edges_.size(), false);

    // Mark the reachable temp edges and nodes.
    for (int i = temp_structure_->edges_.size() - 1; i >= 0; --i) {
        HNode head = temp_structure_->edge_heads_[i];
        if (head == root()) {
            reachable_nodes[head] = true;
        }
        if (reachable_nodes[head]) {
            reachable_edges[i] = true;
            if (!unary_) {
                vector<HNode> &edge = temp_structure_->edge_tails_[i];
                foreach (HNode node, edge) {
                    reachable_nodes[node] = true;
                }
            } else {
                reachable_nodes[temp_structure_->edge_tails_unary_[i]] = true;
            }
        }
    }


    // Relabel edges and nodes.
    int node_count = 0;
    vector<int> node_mapping(temp_structure_->nodes_.size(),
                             NODE_NULL);
    for (uint i = 0; i < reachable_nodes.size(); ++i) {
        if (reachable_nodes[i]) {
            structure_->nodes_.push_back(node_count);
            node_mapping[i] = node_count;
            node_count++;
        }
    }
    structure_->node_edges_.resize(structure_->nodes_.size());
    int edge_count = 0;
    for (uint i = 0; i < reachable_edges.size(); ++i) {
        if (reachable_edges[i]) {
            temp_structure_->edges_[i] = edge_count;
            structure_->edges_.push_back(edge_count);
            if (!unary_) {
                vector<HNode> tail_nodes;
                foreach (HNode node, temp_structure_->edge_tails_[i]) {
                    tail_nodes.push_back(node_mapping[node]);
                }
                structure_->edge_tails_.push_back(tail_nodes);
            } else {
                structure_->edge_tails_unary_.push_back(
                    node_mapping[temp_structure_->edge_tails_unary_[i]]);
            }
            HNode head = node_mapping[temp_structure_->edge_heads_[i]];
            structure_->edge_heads_.push_back(head);
            structure_->node_edges_[head].push_back(i);
            edge_count++;
        } else {
            temp_structure_->edges_[i] = EDGE_NULL;
        }
    }
    root_ = node_mapping[root_];
    temp_structure_->edge_tails_.clear();
    temp_structure_->edge_heads_.clear();
}
