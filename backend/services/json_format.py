import re

def normalize(data):
    # Address logic: handle string, list of dicts, or dict
    addr_raw = data.get("address", "")
    if isinstance(addr_raw, list):
        all_parts = []
        for item in addr_raw:
            if isinstance(item, dict):
                inner = [str(v) for v in item.values() if v and str(v).strip()]
                all_parts.append(" ".join(inner))
            elif item:
                all_parts.append(str(item))
        address = ", ".join(all_parts)
    elif isinstance(addr_raw, dict):
        address = ", ".join(str(v) for v in addr_raw.values() if v and str(v).strip())
    else:
        address = str(addr_raw)

    # Total logic: handle dictionary by summing specific numeric keys
    total_raw = data.get("total", "0")
    if isinstance(total_raw, dict):
        # We extract all potential numeric values and tax values
        # We try to find the best "total" by looking for price+tax pairs
        extracted_sums = []
        
        def find_sums(obj):
            if isinstance(obj, dict):
                price = 0.0
                tax = 0.0
                found_any = False
                for k, v in obj.items():
                    k_low = k.lower()
                    if isinstance(v, (str, int, float)):
                        try:
                            val = float(str(v).replace(",", ".").replace("$", "").strip())
                            # Identify if it's a tax or a base price
                            if "tax" in k_low:
                                tax += val
                                found_any = True
                            elif any(kw in k_low for kw in ["price", "amount", "total", "sub"]):
                                price = max(price, val) # Take the largest 'price' at this level
                                found_any = True
                        except: pass
                    elif isinstance(v, (dict, list)):
                        find_sums(v)
                
                if found_any:
                    extracted_sums.append(price + tax)
            elif isinstance(obj, list):
                for item in obj:
                    find_sums(item)

        find_sums(total_raw)
        if extracted_sums:
            # Usually the largest sum found in the hierarchy is the final total
            total = f"{max(extracted_sums):.2f}"
        else:
            total = "0.00"
    else:
        total_str = str(total_raw).replace(",", ".").replace("$", "").replace(" ", "").strip()
        # Validation: If it's a very long string of digits (> 7) without decimals,
        # it's likely a hallucinated ID rather than a price.
        if re.match(r"^\d{7,}$", total_str):
            total = "0.00"
        else:
            total = total_str

    # Date logic: robust conversion to YY.MM.DD
    date_raw = str(data.get("date", ""))
    nums = re.findall(r"\d+", date_raw)
    if len(nums) >= 3:
        # Check for YYYY-MM-DD or DD-MM-YYYY or YY-MM-DD
        y, m, d = None, None, None
        if len(nums[0]) == 4: # YYYY
            y, m, d = nums[0], nums[1], nums[2]
        elif len(nums[2]) == 4: # ...YYYY
            d, m, y = nums[0], nums[1], nums[2]
        elif len(nums[0]) == 2 and len(nums[1]) == 2 and len(nums[2]) == 2: # YY-MM-DD
            y, m, d = nums[0], nums[1], nums[2]
        
        if y and m and d:
            date_raw = f"{y[-2:]}.{m.zfill(2)}.{d.zfill(2)}"

    return {
        "company": str(data.get("company", "")),
        "date": date_raw,
        "address": address,
        "total": total
    }

def extract_json_block(text):
    # Find the very first '{'
    start = text.find('{')
    if start == -1:
        return None
    
    # Try to find a balanced block
    stack = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            stack += 1
        elif text[i] == '}':
            stack -= 1
            if stack == 0:
                return text[start:i+1]
    
    # If no balanced block found, it's likely truncated.
    # Return from start to the end and let repair_json handle it.
    return text[start:]

def repair_json(json_str):
    if not json_str: return None
    
    # 1. Clean up potential trailing garbage
    json_str = json_str.strip()
    
    # 2. Try to balance braces
    # Count open/close braces
    open_braces = json_str.count('{')
    close_braces = json_str.count('}')
    
    if open_braces > close_braces:
        # If it ends with a comma, remove it before adding braces
        temp = json_str
        if temp.endswith(','):
            temp = temp[:-1]
        
        # Try adding missing braces one by one
        for _ in range(open_braces - close_braces):
            temp += "}"
            try:
                return json.loads(temp)
            except:
                pass
    
    # Final attempt to just fix the current string
    try:
        return json.loads(json_str)
    except:
        return None
