#include <string>
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <vector>
#include "xapian.h"

using namespace std;
using namespace Xapian;

bool isValidPoint(double x, double y);

class CDistanceKeyMaker : public KeyMaker 
{
public:
	CDistanceKeyMaker(double x, double y, bool reverseFlag = false, int slot_y = 1, int slot_x = 2) : m_y(y), m_x(x), m_reverseFlag(reverseFlag), m_slot_y(slot_y), m_slot_x(slot_x) {}
	string operator() (const Xapian::Document &doc) const;
private:
	double m_x;
	double m_y;
	int m_slot_x;
	int m_slot_y;
	bool m_reverseFlag;
};

/*
typedef string (*CALLBACK_SPECIALFUNC)(const Xapian::Document &doc, void *para);
class CCustomizeMultiKeyMaker : public MultiValueKeyMaker 
{
public:
	CCustomizeMultiKeyMaker(Xapian::valueno specialSlot = -1, CALLBACK_SPECIALFUNC specialFunc = NULL, void *specialPara = NULL) : m_specialSlot(specialSlot), m_specialFunc(specialFunc), m_specialPara(specialPara){}
	string operator() (const Xapian::Document &doc) const;
private:
	Xapian::valueno m_specialSlot;
	CALLBACK_SPECIALFUNC m_specialFunc;
	void *m_specialPara;

};*/

class CCustomizeMultiKeyMaker : public KeyMaker 
{
	std::vector<std::pair<Xapian::valueno, bool> > slots;
public:
	CCustomizeMultiKeyMaker(double x = 0.0, double y = 0.0, int slot_y = -1, int slot_x = -1, Xapian::valueno specialSlot = -1) : m_y(y), m_x(x), m_slot_y(slot_y), m_slot_x(slot_x), m_specialSlot(specialSlot) {}
	template <class Iterator>
    CCustomizeMultiKeyMaker(Iterator begin, Iterator end) { while (begin != end) add_value(*begin++); }
	string callback_distance(const Xapian::Document &doc, bool reverseFlag = false) const;
	string operator() (const Xapian::Document &doc) const;
	void add_value(Xapian::valueno slot, bool reverse = false) { slots.push_back(std::make_pair(slot, reverse)); }
private:
	double m_x;
	double m_y;
	int m_slot_x;
	int m_slot_y;
	Xapian::valueno m_specialSlot;
};
