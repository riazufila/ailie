--
-- PostgreSQL database dump
--

-- Dumped from database version 13.3
-- Dumped by pg_dump version 13.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: equipments; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.equipments (
    equip_id bigint NOT NULL,
    equip_name text NOT NULL,
    equip_star integer NOT NULL,
    equip_exclusive boolean NOT NULL,
    equip_pickup boolean DEFAULT false NOT NULL,
    equip_stats json,
    equip_buffs json,
    equip_skill json,
    equip_instant_triggers json,
    equip_triggers json
);


ALTER TABLE public.equipments OWNER TO riazufila;

--
-- Name: equipments_acquired; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.equipments_acquired (
    equip_acquired_id bigint NOT NULL,
    equip_id bigint NOT NULL,
    inventory_id bigint NOT NULL,
    equip_acquired_exp bigint DEFAULT 0 NOT NULL,
    equip_acquired_limit_break integer DEFAULT 0 NOT NULL,
    equip_acquired_roll integer DEFAULT 10 NOT NULL
);


ALTER TABLE public.equipments_acquired OWNER TO riazufila;

--
-- Name: equipments_acquired_equip_acquired_id_seq; Type: SEQUENCE; Schema: public; Owner: riazufila
--

ALTER TABLE public.equipments_acquired ALTER COLUMN equip_acquired_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.equipments_acquired_equip_acquired_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: equipments_equip_id_seq; Type: SEQUENCE; Schema: public; Owner: riazufila
--

ALTER TABLE public.equipments ALTER COLUMN equip_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.equipments_equip_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: guardians; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.guardians (
    guardian_id bigint NOT NULL,
    guardian_username text,
    guild_id bigint,
    guardian_position text,
    guardian_gems bigint DEFAULT 0 NOT NULL,
    guardian_trophy bigint DEFAULT 0 NOT NULL,
    guardian_summon_count integer DEFAULT 0 NOT NULL,
    guardian_wins integer DEFAULT 0 NOT NULL,
    guardian_losses integer DEFAULT 0 NOT NULL,
    guardian_hourly timestamp with time zone,
    guardian_daily timestamp with time zone,
    guardian_daily_count integer DEFAULT 0 NOT NULL,
    guardian_exp bigint DEFAULT 0 NOT NULL,
    guardian_gambled_gems bigint DEFAULT 0 NOT NULL,
    guardian_spent_gems bigint DEFAULT 0 NOT NULL,
    guardian_won_gambled_gems bigint DEFAULT 0 NOT NULL,
    guardian_won_gambled_count bigint DEFAULT 0 NOT NULL,
    guardian_lose_gambled_gems bigint DEFAULT 0 NOT NULL,
    guardian_lose_gambled_count bigint DEFAULT 0 NOT NULL,
    guardian_gamble_count integer DEFAULT 0 NOT NULL,
    guardian_claim bigint DEFAULT 0,
    guardian_arena boolean DEFAULT false
);


ALTER TABLE public.guardians OWNER TO riazufila;

--
-- Name: guilds; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.guilds (
    guild_id bigint NOT NULL,
    guild_name text NOT NULL
);


ALTER TABLE public.guilds OWNER TO riazufila;

--
-- Name: heroes; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.heroes (
    hero_id bigint NOT NULL,
    hero_name text NOT NULL,
    hero_star integer NOT NULL,
    hero_pickup boolean DEFAULT false NOT NULL,
    equip_id bigint,
    hero_stats json,
    hero_buffs json,
    hero_skill json,
    hero_triggers json
);


ALTER TABLE public.heroes OWNER TO riazufila;

--
-- Name: heroes_acquired; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.heroes_acquired (
    hero_acquired_id bigint NOT NULL,
    hero_id bigint NOT NULL,
    inventory_id bigint NOT NULL,
    hero_acquired_exp bigint DEFAULT 0 NOT NULL,
    hero_acquired_limit_break integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.heroes_acquired OWNER TO riazufila;

--
-- Name: heroes_acquired_hero_acquired_id_seq; Type: SEQUENCE; Schema: public; Owner: riazufila
--

ALTER TABLE public.heroes_acquired ALTER COLUMN hero_acquired_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.heroes_acquired_hero_acquired_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: heroes_hero_id_seq; Type: SEQUENCE; Schema: public; Owner: riazufila
--

ALTER TABLE public.heroes ALTER COLUMN hero_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.heroes_hero_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: inventories; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.inventories (
    inventory_id bigint NOT NULL,
    guardian_id bigint NOT NULL
);


ALTER TABLE public.inventories OWNER TO riazufila;

--
-- Name: inventories_inventory_id_seq; Type: SEQUENCE; Schema: public; Owner: riazufila
--

ALTER TABLE public.inventories ALTER COLUMN inventory_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.inventories_inventory_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: items; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.items (
    item_id bigint NOT NULL,
    item_name text NOT NULL,
    item_price integer NOT NULL,
    item_description text
);


ALTER TABLE public.items OWNER TO riazufila;

--
-- Name: items_acquired; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.items_acquired (
    item_acquired_id bigint NOT NULL,
    item_id bigint NOT NULL,
    inventory_id bigint NOT NULL,
    item_acquired_quantity bigint DEFAULT 0 NOT NULL
);


ALTER TABLE public.items_acquired OWNER TO riazufila;

--
-- Name: items_acquired_item_acquired_id_seq; Type: SEQUENCE; Schema: public; Owner: riazufila
--

ALTER TABLE public.items_acquired ALTER COLUMN item_acquired_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.items_acquired_item_acquired_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: items_item_id_seq; Type: SEQUENCE; Schema: public; Owner: riazufila
--

ALTER TABLE public.items ALTER COLUMN item_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.items_item_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: teams; Type: TABLE; Schema: public; Owner: riazufila
--

CREATE TABLE public.teams (
    team_id bigint NOT NULL,
    team_key text NOT NULL,
    team_hero bigint[] NOT NULL,
    guardian_id bigint NOT NULL
);


ALTER TABLE public.teams OWNER TO riazufila;

--
-- Name: teams_team_id_seq; Type: SEQUENCE; Schema: public; Owner: riazufila
--

ALTER TABLE public.teams ALTER COLUMN team_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.teams_team_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: equipments_acquired equipments_acquired_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.equipments_acquired
    ADD CONSTRAINT equipments_acquired_pkey PRIMARY KEY (equip_acquired_id);


--
-- Name: equipments equipments_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.equipments
    ADD CONSTRAINT equipments_pkey PRIMARY KEY (equip_id);


--
-- Name: guardians guardians_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.guardians
    ADD CONSTRAINT guardians_pkey PRIMARY KEY (guardian_id);


--
-- Name: guilds guilds_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.guilds
    ADD CONSTRAINT guilds_pkey PRIMARY KEY (guild_id);


--
-- Name: heroes_acquired heroes_acquired_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.heroes_acquired
    ADD CONSTRAINT heroes_acquired_pkey PRIMARY KEY (hero_acquired_id);


--
-- Name: heroes heroes_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.heroes
    ADD CONSTRAINT heroes_pkey PRIMARY KEY (hero_id);


--
-- Name: inventories inventories_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.inventories
    ADD CONSTRAINT inventories_pkey PRIMARY KEY (inventory_id);


--
-- Name: items_acquired items_acquired_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.items_acquired
    ADD CONSTRAINT items_acquired_pkey PRIMARY KEY (item_acquired_id);


--
-- Name: items items_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_pkey PRIMARY KEY (item_id);


--
-- Name: teams teams_pkey; Type: CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_pkey PRIMARY KEY (team_id);


--
-- Name: equipments_acquired equipments_equip_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.equipments_acquired
    ADD CONSTRAINT equipments_equip_id_fkey FOREIGN KEY (equip_id) REFERENCES public.equipments(equip_id);


--
-- Name: heroes equipments_equip_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.heroes
    ADD CONSTRAINT equipments_equip_id_fkey FOREIGN KEY (equip_id) REFERENCES public.equipments(equip_id) NOT VALID;


--
-- Name: inventories guardians_guardian_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.inventories
    ADD CONSTRAINT guardians_guardian_id_fkey FOREIGN KEY (guardian_id) REFERENCES public.guardians(guardian_id) NOT VALID;


--
-- Name: teams guardians_guardian_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT guardians_guardian_id_fkey FOREIGN KEY (guardian_id) REFERENCES public.guardians(guardian_id);


--
-- Name: guardians guilds_guild_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.guardians
    ADD CONSTRAINT guilds_guild_id_fkey FOREIGN KEY (guild_id) REFERENCES public.guilds(guild_id) NOT VALID;


--
-- Name: heroes_acquired heroes_hero_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.heroes_acquired
    ADD CONSTRAINT heroes_hero_id_fkey FOREIGN KEY (hero_id) REFERENCES public.heroes(hero_id);


--
-- Name: heroes_acquired inventories_inventory_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.heroes_acquired
    ADD CONSTRAINT inventories_inventory_id_fkey FOREIGN KEY (inventory_id) REFERENCES public.inventories(inventory_id) NOT VALID;


--
-- Name: equipments_acquired inventories_inventory_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.equipments_acquired
    ADD CONSTRAINT inventories_inventory_id_fkey FOREIGN KEY (inventory_id) REFERENCES public.inventories(inventory_id) NOT VALID;


--
-- Name: items_acquired inventories_inventory_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.items_acquired
    ADD CONSTRAINT inventories_inventory_id_fkey FOREIGN KEY (inventory_id) REFERENCES public.inventories(inventory_id) NOT VALID;


--
-- Name: items_acquired items_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: riazufila
--

ALTER TABLE ONLY public.items_acquired
    ADD CONSTRAINT items_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(item_id) NOT VALID;


--
-- PostgreSQL database dump complete
--

