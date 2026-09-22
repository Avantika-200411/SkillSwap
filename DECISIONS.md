# SkillSwap — Product Decisions

## DP1 — What happens after a creator declines a booking?

When a creator declines a booking, the client can see the booking status as **Declined**. The client is also given an option to return to the marketplace and find another gig instead of being left at a dead end.

## DP2 — Can a gig accept a new booking while another is Pending?

Yes. Multiple booking requests can remain **Pending** because a pending request is not a confirmed booking. Once the creator accepts one request, that booking becomes **Accepted**, the gig becomes unavailable, and all other pending requests for that gig are automatically declined to prevent double booking.

## DP3 — How are gigs ranked?

Available gigs are shown with the **newest gigs first**. Search and category filters narrow the marketplace results, while the newest matching gigs appear at the top so recently posted services are easier to discover.