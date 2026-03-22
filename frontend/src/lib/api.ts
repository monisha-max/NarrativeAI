import axios from "axios";
import type { Dossier, DossierListResponse } from "@/types/dossier";
import type { EntityGraph } from "@/types/entity";
import type { StoryDNA } from "@/types/archetype";
import type { BriefingRequest, BriefingResponse, GuidedPrompt } from "@/types/briefing";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const client = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

export const api = {
  // Dossiers
  async getDossiers(): Promise<DossierListResponse> {
    const { data } = await client.get("/dossiers/");
    return data;
  },

  async getDossier(slug: string): Promise<Dossier> {
    const { data } = await client.get(`/dossiers/${slug}`);
    return data;
  },

  async createDossier(title: string, description?: string): Promise<Dossier> {
    const { data } = await client.post("/dossiers/", { title, description });
    return data;
  },

  // Entities
  async getEntityGraph(dossierSlug: string): Promise<EntityGraph> {
    const { data } = await client.get(`/entities/graph/${dossierSlug}`);
    return data;
  },

  // Story DNA
  async getStoryDNA(dossierSlug: string): Promise<StoryDNA> {
    const { data } = await client.get(`/stories/dna/${dossierSlug}`);
    return data;
  },

  // Briefing
  async getGuidedPrompts(): Promise<Record<string, GuidedPrompt>> {
    const { data } = await client.get("/briefing/prompts");
    return data;
  },

  async getBriefing(slug: string, request: BriefingRequest): Promise<BriefingResponse> {
    const { data } = await client.post(`/briefing/${slug}`, request);
    return data;
  },

  // Search
  async search(query: string, dossier?: string) {
    const { data } = await client.get("/search/", { params: { q: query, dossier } });
    return data;
  },

  // Ripples
  async getRipples(dossierSlug: string) {
    const { data } = await client.get(`/ripples/${dossierSlug}`);
    return data;
  },

  // Delta
  async getDelta(userId: string, dossierSlug: string) {
    const { data } = await client.get(`/delta/${userId}/${dossierSlug}`);
    return data;
  },

  async getAllDeltas(userId: string) {
    const { data } = await client.get(`/delta/${userId}/all`);
    return data;
  },

  // Archetypes
  async getArchetypes() {
    const { data } = await client.get("/stories/archetypes");
    return data;
  },

  // Contrarian analysis
  async getContrarian(dossierSlug: string) {
    const { data } = await client.get(`/dossiers/${dossierSlug}/contrarian`);
    return data;
  },

  // Claims vs facts
  async getClaims(dossierSlug: string) {
    const { data } = await client.get(`/dossiers/${dossierSlug}/claims`);
    return data;
  },

  // Vernacular translation
  async translate(text: string, targetLang: string, userType: string = "retail_investor") {
    const { data } = await client.post("/briefing/translate", { text, target_lang: targetLang, user_type: userType });
    return data;
  },

  // Health check
  async healthCheck() {
    const { data } = await client.get("/../../health");
    return data;
  },
};
