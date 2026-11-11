from tablets_devops.analysis import summarize


def test_ea1_statistics(dataset):
    result = summarize(dataset)
    assert (result["records"], result["brands"]) == (80, 9)
    assert (result["in_stock"], result["out_of_stock"]) == (44, 36)
    assert result["median_cop"] == 3179945.0
    assert result["minimum_cop"] == 389900.0
    assert result["maximum_cop"] == 12629010.0
    assert result["refurbished_in_title"] == 12
    assert sum(r["count"] for r in result["by_brand"]) == 80
