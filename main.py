"""A rewrite of the banking script."""
import sheets_api
import sheet
import bank


MATCH_WEIGHTS = {"date diff": 50, "amount diff": 50, "balance diff": 5, "desc diff": 30}
MATCH_RANGES = {"date diff": 5, "amount diff": 1, "balance diff": 200, "desc diff": 1}
THRESHOLD = 0.5
PROMPT_NEAR_MATCHES = True


def _get_match_factors(sheet_entry, bank_entry, accounts):
    """Get the factors which contribute to a match."""

    factors = {}

    factors["date diff"] = (bank_entry["Date"] - sheet_entry["Date"]).days

    # Find amount which isn't blank for this entry
    for account in accounts:
        sheet_amount = sheet_entry[account]
        sheet_balance = sheet_entry[account + " Running"]
        if sheet_amount != "":
            break

    # TODO: Remove after auto updating balances implemented 
    if not sheet_balance:
        sheet_balance = 0

    factors["amount diff"] = bank_entry["Amount"] - sheet_amount

    bank_balance = bank_entry["Balance"]

    factors["balance diff"] = 0
    if bank_balance != "":
        factors["balance diff"] = bank_balance - sheet_balance

    sheet_desc = sheet_entry["Bank_Listed_Item"]
    bank_desc = bank_entry["Description"]

    factors["desc diff"] = sheet_desc != bank_desc

    return factors


def score_match(sheet_entry, bank_entry, accounts):
    """Score based on the factors which contribute to a match and their weights."""
    factors = _get_match_factors(sheet_entry, bank_entry, accounts)

    score = 0
    for factor in factors:
        score += min(abs(factors[factor] / MATCH_RANGES[factor]), 1) * (
            MATCH_WEIGHTS[factor] / 100
        )

    return score


def _get_closest_score(scores, matched_indexes):
    """Find the closest score which is not already accounted for."""
    closest_score = None
    closest_ind = None
    for score_ind, score in enumerate(scores):
        if score_ind in matched_indexes:
            continue
        elif isinstance(closest_score, type(None)) or score < closest_score:
            closest_score = score
            closest_ind = score_ind
            if closest_score == 0:
                break

    return closest_ind


def _find_perfect_matches(sheet_entries, bank_entries, fields, accounts):
    """Find indices of perfect matches and all scores."""
    all_scores = []
    matched_sheet_indices = []
    matched_bank_indices = []
    # Find all perfect matches
    for bank_ind, bank_entry in enumerate(bank_entries):
        scores = []
        # Start matching
        for ind, sheet_entry in enumerate(sheet_entries):
            if ind in matched_sheet_indices:
                # Already been matched to a bank entry
                scores.append(-1)
                continue
            score = score_match(sheet_entry, bank_entry, accounts)
            scores.append(score)
            if score == 0:
                # Found perfect match, stop searching
                break

        all_scores.append(scores)

        # Determine best score
        closest_match_ind = _get_closest_score(scores, matched_sheet_indices)
        closest_score = scores[closest_match_ind]

        if closest_score == 0:
            # Perfect match
            matched_sheet_indices.append(closest_match_ind)
            matched_bank_indices.append(bank_ind)

    return matched_sheet_indices, matched_bank_indices, all_scores


def _find_imperfect_matches(
    sheet_entries,
    bank_entries,
    all_scores,
    matched_bank_indices,
    matched_sheet_indices,
    fields,
    accounts,
):
    """Update matched indices to include imperfect matches."""
    for ind, bank_entry in enumerate(bank_entries):
        if ind in matched_bank_indices:
            # Already has perfect match
            continue

        scores = all_scores[ind]
        closest_match_ind = _get_closest_score(scores, matched_sheet_indices)
        closest_score = scores[closest_match_ind]
        closest_match = sheet_entries[closest_match_ind]

        if closest_score < THRESHOLD:
            print(f"NEAR MATCH: {closest_score} for", bank_entry, closest_match)
            if PROMPT_NEAR_MATCHES:
                match = input("Do these match? (y): ")
                if match == "y":
                    print("Updated matches")
                    matched_bank_indices.append(ind)
                    matched_sheet_indices.append(closest_match_ind)
                    sheet.update_entry(closest_match_ind, bank_entry, fields, accounts)


def find_new_entries(sheet_entries, bank_entries, fields, accounts):
    """Find all entries not already in the sheet."""

    def entry_key(entry):
        return entry["Date"]

    # Sort entries by date
    sheet_entries = sorted(sheet_entries, key=entry_key)
    bank_entries = sorted(bank_entries, key=entry_key)

    matches = _find_perfect_matches(sheet_entries, bank_entries, fields, accounts)
    matched_sheet_indices, matched_bank_indices, all_scores = matches

    _find_imperfect_matches(
        sheet_entries,
        bank_entries,
        all_scores,
        matched_bank_indices,
        matched_sheet_indices,
        fields,
        accounts,
    )

    all_bank_indices = set(range(len(bank_entries)))
    unmatched_indices = all_bank_indices - set(matched_bank_indices)

    unmatched = []
    for ind in unmatched_indices:
        unmatched.append(bank_entries[ind])

    return unmatched


def main():
    """Run the program."""
    sheets_api.authorize()

    accounts = sheet.get_accounts()

    sheet_fields = sheet.get_fields()
    sheet_entries = sheet.get_entries(sheet_fields, accounts)

    bank_fields = bank.get_fields()
    bank_entries = bank.get_entries(bank_fields)

    new_entries = find_new_entries(sheet_entries, bank_entries, sheet_fields, accounts)
    sheet.add_entries(new_entries, sheet_fields, accounts)


if __name__ == "__main__":
    main()
