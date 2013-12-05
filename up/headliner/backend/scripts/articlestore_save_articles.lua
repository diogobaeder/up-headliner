local articles = cjson.decode(ARGV[1])
local num_added = 0

for i, article in ipairs(articles) do
    if redis.call("SISMEMBER", article["set_key"], article["member"]["url"]) == 0 then
        redis.call("ZADD", article["sorted_key"], article["score"], cjson.encode(article["member"]))
        redis.call("SADD", article["set_key"], article["member"]["url"])
        num_added = num_added + 1
    end
end

return num_added
