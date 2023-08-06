#include <math.h>
#include <string>
#include "xapian.h"
#include "config.h"
#include "distanceKeyMaker.h"
#include <iostream>

using namespace Xapian;

bool isValidPoint(double x, double y)
{
    bool bRet = false;
    if ((y >= 3.86 && y <= 53.56) && (x >= 73.66 && x <= 135.05))
    {
        bRet = true;
    }
    return bRet;
}

string CDistanceKeyMaker::operator() (const Xapian::Document &doc) const
{
    string sy = doc.get_value(m_slot_y);
    string sx = doc.get_value(m_slot_x);
    
    double y = atof(sy.c_str());
    double x = atof(sx.c_str());

    int dis = 0;
    if(isValidPoint(x, y) && isValidPoint(m_x, m_y))
    {
        dis = int(100000 * sqrt(pow(y - m_y, 2) + pow(x - m_x, 2))) / 1000 * 1000;
    }
    else
    {
        if (m_reverseFlag)
        {
            //reverses the sort order
            dis = 0;
        }
        else
        {
            dis = 5000000;
        }

    }
    string value = sortable_serialise(dis);

    return value;
}


string CCustomizeMultiKeyMaker::operator() (const Xapian::Document &doc) const
{
    string result;

    vector<pair<Xapian::valueno, bool> >::const_iterator i = slots.begin();
    // Don't crash if slots is empty.
    if (rare(i == slots.end())) return result;

    size_t last_not_empty_forwards = 0;
    while (true) {
    // All values (except for the last if it's sorted forwards) need to
    // be adjusted.
    //
    // FIXME: allow Xapian::BAD_VALUENO to mean "relevance?"
    string v = "";
    if (i->first == m_specialSlot)
    {
        v = callback_distance(doc, i->second);
    }
    else
    {
        v = doc.get_value(i->first);
    }
    bool reverse_sort = i->second;

    if (reverse_sort || !v.empty())
        last_not_empty_forwards = result.size();

    if (++i == slots.end() && !reverse_sort) {
        if (v.empty()) {
        // Trim off all the trailing empty forwards values.
        result.resize(last_not_empty_forwards);
        } else {
        // No need to adjust the last value if it's sorted forwards.
        result += v;
        }
        break;
    }

    if (reverse_sort) {
        // For a reverse ordered value, we subtract each byte from '\xff',
        // except for '\0' which we convert to "\xff\0".  We insert
        // "\xff\xff" after the encoded value.
        for (string::const_iterator j = v.begin(); j != v.end(); ++j) {
        unsigned char ch(*j);
        result += char(255 - ch);
        if (ch == 0) result += '\0';
        }
        result.append("\xff\xff", 2);
        if (i == slots.end()) break;
        last_not_empty_forwards = result.size();
    } else {
        // For a forward ordered value (unless it's the last value), we
        // convert any '\0' to "\0\xff".  We insert "\0\0" after the
        // encoded value.
        string::size_type j = 0, nul;
        while ((nul = v.find('\0', j)) != string::npos) {
        ++nul;
        result.append(v, j, nul - j);
        result += '\xff';
        j = nul;
        }
        result.append(v, j, string::npos);
        if (!v.empty())
        last_not_empty_forwards = result.size();
        result.append("\0", 2);
    }
    }
    return result;
}

string CCustomizeMultiKeyMaker::callback_distance(const Xapian::Document &doc, bool reverseFlag) const
{
    string sy = doc.get_value(m_slot_y);
    string sx = doc.get_value(m_slot_x);
    
    double y = atof(sy.c_str());
    double x = atof(sx.c_str());

    int dis = 0;
    if(isValidPoint(x, y) && isValidPoint(m_x, m_y))
    {
        dis = int(100000 * sqrt(pow(y - m_y, 2) + pow(x - m_x, 2))) / 1000 * 1000;
    }
    else
    {
        if (reverseFlag)
        {
            //reverses the sort order
            dis = 0;
        }
        else
        {
            dis = 5000000;
        }

    }
    string value = sortable_serialise(dis);

    return value;
}

