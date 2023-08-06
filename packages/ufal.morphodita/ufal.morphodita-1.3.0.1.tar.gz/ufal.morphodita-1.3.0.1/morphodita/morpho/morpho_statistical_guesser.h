// This file is part of MorphoDiTa.
//
// Copyright 2013 by Institute of Formal and Applied Linguistics, Faculty of
// Mathematics and Physics, Charles University in Prague, Czech Republic.
//
// MorphoDiTa is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as
// published by the Free Software Foundation, either version 3 of
// the License, or (at your option) any later version.
//
// MorphoDiTa is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with MorphoDiTa.  If not, see <http://www.gnu.org/licenses/>.

#pragma once

#include "../common.h"
#include "morpho.h"
#include "../utils/binary_decoder.h"
#include "../utils/persistent_unordered_map.h"

namespace ufal {
namespace morphodita {

class morpho_statistical_guesser {
 public:
  void load(binary_decoder& data);
  typedef vector<string> used_rules;
  void analyze(string_piece form, vector<tagged_lemma>& lemmas, used_rules* used);

 private:
  vector<string> tags;
  unsigned default_tag;
  persistent_unordered_map rules;
};

} // namespace morphodita
} // namespace ufal
