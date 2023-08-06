template<typename StatSem>
struct NodeScore {
    NodeScore()
            :
            count(-1),
            edge(-1),
            back(0),
            score(StatSem::zero()) {}

    NodeScore(int _count, HEdge _edge,
              typename StatSem::ValType _score)
            :
            count(_count),
            edge(_edge),
            back(0),
            score(_score) {}

    NodeScore(int _count, HEdge _edge, int i, int j,
              typename StatSem::ValType _score)
            :
            count(_count),
            edge(_edge),
            back(2),
            score(_score) {
        back[0] = i;
        back[1] = j;
    }

    int count;
    HEdge edge;
    vector<int> back;
    typename StatSem::ValType score;
};

template<typename S>
Hyperpath *count_constrained_viterbi(
    const Hypergraph *graph,
    const HypergraphPotentials<S> &weight_potentials,
    const HypergraphPotentials<CountingPotential> &count_potentials,
    int limit) {

  weight_potentials.check(*graph);
  count_potentials.check(*graph);

  vector<vector<NodeScore<S> > > chart(graph->nodes().size());

  foreach (HNode node, graph->nodes()) {
      if (graph->terminal(node)) {
          chart[node].push_back(
            NodeScore<S>(0, -1, S::one()));
    }
    // Bucket edges.
    vector<NodeScore<S> > counts(limit + 1);
    foreach (HEdge edge, graph->edges(node)) {
        bool unary = graph->tail_nodes(edge) == 1;
        HNode left_node = graph->tail_node(edge, 0);

        int start_count = count_potentials.score(edge);
        typename S::ValType start_score = weight_potentials.score(edge);
        for (int i = 0; i < chart[left_node].size(); ++i) {
            int total = start_count + chart[left_node][i].count;
            typename S::ValType total_score =
                    S::times(start_score,
                                   chart[left_node][i].score);
            if (total > limit) continue;
            if (unary) {
                if (total_score > counts[total].score) {
                    counts[total] =
                            NodeScore<S>(total, edge, i, -1, total_score);
                }
            } else {
                HNode right_node = graph->tail_node(edge, 1);
                for (int j = 0; j < chart[right_node].size(); ++j) {
                    int total = start_count + chart[left_node][i].count
                            + chart[right_node][j].count;
                    typename S::ValType final_score =
                            S::times(total_score,
                                           chart[right_node][j].score);

                    if (total > limit) continue;
                    if (final_score > counts[total].score) {
                        counts[total] =
                                NodeScore<S>(total,
                                             edge,
                                             i,
                                             j,
                                             final_score);
                    }
                }
            }
        }
    }

    // Compute scores.
    for (int count = 0; count <= limit; ++count) {
        if (counts[count].edge == -1) continue;
        chart[node].push_back(counts[count]);
    }
  }

  // Collect backpointers.
  vector<HEdge> path;
  vector<HNode> node_path;
  queue<pair<HNode, int> > to_examine;
  int result = -1;
  int i = -1;
  foreach (NodeScore<S> score, chart[graph->root()]) {
      ++i;
      if (score.count == limit) {
          result = i;
      }
  }

  to_examine.push(pair<HNode, int>(graph->root(), result));
  while (!to_examine.empty()) {
      if (result == -1) break;
      pair<HNode, int> p = to_examine.front();
      HNode node = p.first;
      node_path.push_back(node);
      int position = p.second;

      NodeScore<S> &score = chart[node][position];
      HEdge edge = score.edge;

      to_examine.pop();
      if (edge == -1) {
          assert(graph->terminal(node));
          continue;
      }
      path.push_back(edge);
      for (int i = 0; i < graph->tail_nodes(edge); ++i) {
          HNode node = graph->tail_node(edge, i);
          to_examine.push(pair<HNode, int>(node,
                                           score.back[i]));
      }
  }
  sort(path.begin(), path.end());
  sort(node_path.begin(), node_path.end());
  return new Hyperpath(graph, node_path, path);
}


template Hyperpath *count_constrained_viterbi<LogViterbi>(
    const Hypergraph *graph,
    const HypergraphPotentials<LogViterbi> &weight_potentials,
    const HypergraphPotentials<Counting> &count_potentials,
    int limit);


// template<typename S>
// struct Hypothesis {
//     vector<int> vec;
//     HEdge edge;
//     V score;
// };



// template<typename S>
// void general_kbest(
//     const Hypergraph *graph,
//     const HypergraphPotentials<S> &potentials,
//     KBackPointers *back,
//     int K) {

//     potentials.check(*graph);
//     back->check(graph);

//     foreach (HNode node, graph->nodes()) {
//         for (int k = 0; k < K; ++k) {
//             vector<Hypothesis> edge_hyps(edges().size());
//             foreach (HEdge edge, node->edges()) {

//             }

//             int edge_num = 0;
//             foreach (HEdge edge, node->edges()) {
//                 vector<int> children(edge.tail->size(), 0);
//                 typename S::ValType score = potentials.score(edge);
//                 foreach(HNode node, edge->tail()) {
//                     score = S::times(score, chart_[tail->id()]);
//                 }
//                 Hypothesis hypothesis();

//                 edge_num++;
//             }
//             children[best_edge]++;
//         }

//     }
// }
