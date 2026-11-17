// Generated from evaluation/master_results.json (test set, 458 narratives). Do not edit by hand.
export const COMPANY = "Cedar Ridge Pipeline Services"; // PLACEHOLDER: replace with the real company name

export const CAUSES = [
  { title: "Equipment failure", n: 787, train: 551, syn: 0 },
  { title: "Corrosion failure", n: 657, train: 460, syn: 0 },
  { title: "Material failure of pipe or weld", n: 372, train: 260, syn: 40 },
  { title: "Excavation damage", n: 362, train: 253, syn: 47 },
  { title: "Natural force damage", n: 301, train: 211, syn: 89 },
  { title: "Other outside force damage", n: 210, train: 147, syn: 153 },
  { title: "Other incident cause", n: 190, train: 133, syn: 167 },
  { title: "Incorrect operation", n: 165, train: 115, syn: 185 },
] as const;

export const MODELS = [
  { id: "gru", name: "BiGRU + FastText", who: "Parva", e1: {"acc": 0.524017, "f1": 0.467792, "val": 0.553468, "ep": 14, "eps": 19, "params": null, "pc": [0.5905, 0.621, 0.4727, 0.7879, 0.4615, 0.4364, 0.1143, 0.2581]}, e2: {"acc": 0.600437, "f1": 0.474915, "val": 0.585709, "ep": 12, "eps": 17, "params": null, "pc": [0.7273, 0.664, 0.4835, 0.7805, 0.4471, 0.381, 0.1224, 0.1935]} },
  { id: "lstm", name: "BiLSTM + attention", who: "Muhammad", e1: {"acc": 0.567686, "f1": 0.534712, "val": 0.576963, "ep": 22, "eps": 27, "params": 903688, "pc": [0.5854, 0.7293, 0.5536, 0.789, 0.5057, 0.5556, 0.2449, 0.3143]}, e2: {"acc": 0.565502, "f1": 0.468106, "val": 0.56037, "ep": 17, "eps": 22, "params": 903688, "pc": [0.658, 0.6514, 0.5641, 0.735, 0.5405, 0.3846, 0.0417, 0.1695]} },
  { id: "bert", name: "Frozen BERT", who: "Sakina", e1: {"acc": 0.60262, "f1": 0.553201, "val": 0.582193, "ep": 11, "eps": 16, "params": 6152, "pc": [0.7, 0.6766, 0.4626, 0.7736, 0.5867, 0.5091, 0.2807, 0.4364]}, e2: {"acc": 0.60262, "f1": 0.531046, "val": 0.574507, "ep": 18, "eps": 20, "params": 6152, "pc": [0.6967, 0.6604, 0.4677, 0.7679, 0.5679, 0.5, 0.2128, 0.375]} },
] as const;

export const POOLER = { e1: {"acc": 0.39083, "f1": 0.305058, "val": 0.346388, "ep": 11, "eps": 16, "params": 6152, "pc": [0.5882, 0.4345, 0.2353, 0.3896, 0.2903, 0.274, 0.0, 0.2286]}, e2: {"acc": 0.395197, "f1": 0.321244, "val": 0.373736, "ep": 16, "eps": 20, "params": 6152, "pc": [0.5822, 0.4972, 0.2832, 0.4, 0.3652, 0.2114, 0.0, 0.2308]} } as const;
