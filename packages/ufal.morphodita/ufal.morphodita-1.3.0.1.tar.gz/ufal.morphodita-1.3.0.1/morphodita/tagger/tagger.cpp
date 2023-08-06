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

#include "czech_elementary_features.h"
#include "generic_elementary_features.h"
#include "feature_sequences.h"
#include "perceptron_tagger.h"
#include "tagger.h"
#include "tagger_ids.h"
#include "../utils/file_ptr.h"
#include "../utils/new_unique_ptr.h"

namespace ufal {
namespace morphodita {

tagger* tagger::load(FILE* f) {
  switch (fgetc(f)) {
    case tagger_ids::CZECH2:
      {
        auto res = new_unique_ptr<perceptron_tagger<persistent_feature_sequences<persistent_czech_elementary_features>, 2>>();
        if (res->load(f)) return res.release();
        break;
      }
    case tagger_ids::CZECH3:
      {
        auto res = new_unique_ptr<perceptron_tagger<persistent_feature_sequences<persistent_czech_elementary_features>, 3>>();
        if (res->load(f)) return res.release();
        break;
      }
    case tagger_ids::GENERIC2:
      {
        auto res = new_unique_ptr<perceptron_tagger<persistent_feature_sequences<persistent_generic_elementary_features>, 2>>();
        if (res->load(f)) return res.release();
        break;
      }
    case tagger_ids::GENERIC3:
      {
        auto res = new_unique_ptr<perceptron_tagger<persistent_feature_sequences<persistent_generic_elementary_features>, 3>>();
        if (res->load(f)) return res.release();
        break;
      }
    case tagger_ids::GENERIC4:
      {
        auto res = new_unique_ptr<perceptron_tagger<persistent_feature_sequences<persistent_generic_elementary_features>, 4>>();
        if (res->load(f)) return res.release();
        break;
      }
  }

  return nullptr;
}

tagger* tagger::load(const char* fname) {
  file_ptr f = fopen(fname, "rb");
  if (!f) return nullptr;

  return load(f);
}

tokenizer* tagger::new_tokenizer() const {
  auto morpho = get_morpho();
  return morpho ? morpho->new_tokenizer() : nullptr;
}

} // namespace morphodita
} // namespace ufal
